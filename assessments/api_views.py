from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Question, Test, Attempt, Profile
from .services import compute_scores


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for tests.
    """
    queryset = Test.objects.filter(is_active=True)
    
    def list(self, request):
        tests = self.get_queryset()
        data = []
        for test in tests:
            data.append({
                'id': test.id,
                'name': test.name,
                'description': test.description,
                'duration_minutes': test.duration_minutes,
                'question_count': test.test_questions.count()
            })
        return Response(data)
    
    def retrieve(self, request, pk=None):
        try:
            test = self.get_queryset().get(pk=pk)
            questions = []
            for tq in test.test_questions.all():
                q = tq.question
                questions.append({
                    'id': q.id,
                    'text': q.text,
                    'category': q.category,
                    'options': {
                        'A': q.option_a,
                        'B': q.option_b,
                        'C': q.option_c,
                        'D': q.option_d
                    }
                })
            
            return Response({
                'id': test.id,
                'name': test.name,
                'description': test.description,
                'duration_minutes': test.duration_minutes,
                'questions': questions
            })
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)


class AttemptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for test attempts.
    """
    queryset = Attempt.objects.all()
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Attempt.objects.filter(user=self.request.user)
        return Attempt.objects.none()
    
    @action(detail=False, methods=['post'])
    def start_test(self, request):
        """Start a new test attempt."""
        test_id = request.data.get('test_id')
        
        if not test_id:
            return Response({'error': 'test_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            test = Test.objects.get(id=test_id, is_active=True)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create new attempt
        attempt = Attempt.objects.create(
            user=request.user,
            test=test,
            status='in_progress'
        )
        
        return Response({
            'attempt_id': attempt.id,
            'test_id': test.id,
            'started_at': attempt.started_at
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit an answer for a question."""
        try:
            attempt = self.get_queryset().get(pk=pk)
        except Attempt.DoesNotExist:
            return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if attempt.status != 'in_progress':
            return Response({'error': 'Attempt is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
        
        question_id = str(request.data.get('question_id'))
        answer = request.data.get('answer')
        
        if not question_id or not answer:
            return Response({'error': 'question_id and answer are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update answers
        attempt.answers[question_id] = answer
        attempt.save()
        
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def complete_test(self, request, pk=None):
        """Complete a test and compute scores."""
        try:
            attempt = self.get_queryset().get(pk=pk)
        except Attempt.DoesNotExist:
            return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if attempt.status != 'in_progress':
            return Response({'error': 'Attempt is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Compute scores
        scores = compute_scores(attempt)
        
        return Response({
            'attempt_id': attempt.id,
            'total_score': attempt.total_score,
            'percentage': attempt.percentage,
            'scores': scores
        })
