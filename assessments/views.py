from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from weasyprint import HTML
import csv
import io
import os
from .models import Question, Test, TestQuestion, Attempt, Profile
from .serializers import (QuestionSerializer, TestSerializer, AttemptSerializer, 
                         SubmitAttemptSerializer)
from .services import compute_scores


# ============ API Views ============

class QuestionViewSet(viewsets.ModelViewSet):
    """API viewset for Question model."""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminUser]


class TestViewSet(viewsets.ModelViewSet):
    """API viewset for Test model."""
    queryset = Test.objects.filter(is_active=True)
    serializer_class = TestSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class AttemptViewSet(viewsets.ModelViewSet):
    """API viewset for Attempt model."""
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Attempt.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_attempt(request):
    """
    Submit an attempt with answers and compute scores.
    """
    serializer = SubmitAttemptSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    test_id = serializer.validated_data['test_id']
    answers = serializer.validated_data['answers']
    
    # Convert string keys to integers
    answers_dict = {int(k): v for k, v in answers.items()}
    
    try:
        test = Test.objects.get(id=test_id, is_active=True)
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Compute scores
    scores = compute_scores(answers_dict)
    
    # Create or update attempt
    attempt = Attempt.objects.create(
        user=request.user,
        test=test,
        status='completed',
        completed_at=timezone.now(),
        answers=answers_dict,
        dimension_scores=scores['dimension_scores'],
        total_score=scores['total_score'],
        top_dimensions=scores['top_dimensions']
    )
    
    return Response({
        'attempt_id': attempt.id,
        'dimension_scores': scores['dimension_scores'],
        'total_score': scores['total_score'],
        'top_dimensions': scores['top_dimensions']
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def autosave_attempt(request, attempt_id):
    """
    Autosave attempt answers (for timer functionality).
    """
    try:
        attempt = Attempt.objects.get(id=attempt_id, user=request.user)
    except Attempt.DoesNotExist:
        return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if attempt.status != 'in_progress':
        return Response({'error': 'Attempt is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
    
    answers = request.data.get('answers', {})
    # Convert string keys to integers
    answers_dict = {int(k): v for k, v in answers.items()}
    attempt.answers = answers_dict
    attempt.save(update_fields=['answers'])
    
    return Response({'message': 'Autosaved successfully'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def upload_csv(request):
    """
    Admin API endpoint to upload CSV file and import questions.
    """
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    
    try:
        # Read CSV file
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        questions_created = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            text = row.get('text', '').strip()
            dimension = row.get('dimension', '').strip().lower()
            weight = float(row.get('weight', 1.0))
            
            if not text or not dimension:
                errors.append(f'Row {row_num}: Missing text or dimension')
                continue
            
            # Validate dimension
            valid_dimensions = [choice[0] for choice in Question.DIMENSION_CHOICES]
            if dimension not in valid_dimensions:
                errors.append(
                    f'Row {row_num}: Invalid dimension "{dimension}". '
                    f'Valid: {", ".join(valid_dimensions)}'
                )
                continue
            
            Question.objects.create(
                text=text,
                dimension=dimension,
                weight=weight
            )
            questions_created += 1
        
        return Response({
            'message': f'Successfully imported {questions_created} questions',
            'errors': errors
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============ Student Views ============

@login_required
def student_dashboard(request):
    """Student dashboard showing available tests and attempts."""
    tests = Test.objects.filter(is_active=True)
    attempts = Attempt.objects.filter(user=request.user).order_by('-started_at')[:10]
    
    context = {
        'tests': tests,
        'attempts': attempts,
    }
    return render(request, 'assessments/student_dashboard.html', context)


@login_required
def take_test(request, test_id):
    """Take test page with timer and questions."""
    test = get_object_or_404(Test, id=test_id, is_active=True)
    
    # Create a new attempt
    attempt = Attempt.objects.create(
        user=request.user,
        test=test,
        status='in_progress'
    )
    
    # Get test questions in order
    test_questions = test.test_questions.select_related('question').all()
    
    context = {
        'test': test,
        'attempt': attempt,
        'test_questions': test_questions,
    }
    return render(request, 'assessments/take_test.html', context)


@login_required
def view_report(request, attempt_id):
    """View attempt report."""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    context = {
        'attempt': attempt,
    }
    return render(request, 'assessments/report.html', context)


@login_required
def download_pdf_report(request, attempt_id):
    """Generate and download PDF report for an attempt."""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    # Check if PDF already exists
    if attempt.pdf_report_file and os.path.exists(attempt.pdf_report_file.path):
        return FileResponse(
            open(attempt.pdf_report_file.path, 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f'report_attempt_{attempt.id}.pdf'
        )
    
    # Generate PDF
    context = {
        'attempt': attempt,
    }
    html_string = render(request, 'assessments/report.html', context).content.decode('utf-8')
    
    # Create PDF
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    
    # Save PDF to media
    filename = f'reports/report_attempt_{attempt.id}.pdf'
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'wb') as f:
        f.write(pdf_file)
    
    # Update attempt
    attempt.pdf_report_file = filename
    attempt.save(update_fields=['pdf_report_file'])
    
    # Return PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_attempt_{attempt.id}.pdf"'
    return response
