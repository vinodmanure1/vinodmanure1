from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from weasyprint import HTML
from django.template.loader import render_to_string
import os

from .models import Test, Attempt, TestQuestion
from .serializers import (TestSerializer, TestDetailSerializer, AttemptSerializer,
                         AttemptSubmitSerializer, AttemptAutosaveSerializer)
from .services import compute_scores, get_report_paragraph


# DRF ViewSets
class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for tests"""
    queryset = Test.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestDetailSerializer
        return TestSerializer


class AttemptViewSet(viewsets.ModelViewSet):
    """API endpoint for attempts"""
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit test answers and compute scores"""
        serializer = AttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        test_id = serializer.validated_data['test_id']
        answers = serializer.validated_data['answers']
        
        test = get_object_or_404(Test, id=test_id)
        
        # Create or get existing attempt
        attempt, created = Attempt.objects.get_or_create(
            test=test,
            user=request.user,
            completed_at__isnull=True,
            defaults={'raw_answers': answers}
        )
        
        if not created:
            attempt.raw_answers = answers
        
        # Compute scores
        score_data = compute_scores(attempt)
        attempt.scores = score_data['dimension_scores']
        attempt.total_score = score_data['total_score']
        attempt.completed_at = timezone.now()
        attempt.save()
        
        return Response({
            'attempt_id': attempt.id,
            'scores': score_data['dimension_scores'],
            'total_score': score_data['total_score'],
            'top_dimensions': score_data['top_dimensions'],
        })
    
    @action(detail=False, methods=['post'])
    def autosave(self, request):
        """Auto-save partial answers"""
        serializer = AttemptAutosaveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        attempt_id = serializer.validated_data['attempt_id']
        answers = serializer.validated_data['answers']
        
        attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
        attempt.raw_answers = answers
        attempt.save()
        
        return Response({'status': 'saved'})


# Student Views (Server-rendered)
@login_required
def student_dashboard(request):
    """Student dashboard showing available tests and previous attempts"""
    user_profile = request.user.profile if hasattr(request.user, 'profile') else None
    grade = user_profile.grade if user_profile else 9
    
    # Get tests for student's grade
    tests = Test.objects.filter(grade=grade)
    
    # Get student's previous attempts
    attempts = Attempt.objects.filter(user=request.user).select_related('test')
    
    context = {
        'tests': tests,
        'attempts': attempts,
        'user_grade': grade,
    }
    return render(request, 'assessments/dashboard.html', context)


@login_required
def take_test(request, test_id):
    """View for taking a test"""
    test = get_object_or_404(Test, id=test_id)
    
    # Get or create an in-progress attempt
    attempt, created = Attempt.objects.get_or_create(
        test=test,
        user=request.user,
        completed_at__isnull=True,
    )
    
    # Get test questions in order
    test_questions = TestQuestion.objects.filter(test=test).select_related('question').order_by('sequence')
    
    context = {
        'test': test,
        'attempt': attempt,
        'test_questions': test_questions,
    }
    return render(request, 'assessments/take_test.html', context)


@login_required
def generate_report_pdf(request, attempt_id):
    """Generate PDF report for an attempt"""
    attempt = get_object_or_404(Attempt, id=attempt_id)
    
    # Check permissions
    if attempt.user != request.user and not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    # If PDF already exists, return it
    if attempt.pdf_report_file:
        return FileResponse(attempt.pdf_report_file.open('rb'), content_type='application/pdf')
    
    # Get report paragraphs for each dimension
    dimension_reports = {}
    for dimension, score in attempt.scores.items():
        dimension_reports[dimension] = {
            'score': score,
            'student_paragraph': get_report_paragraph(dimension, score, 'student'),
            'parent_paragraph': get_report_paragraph(dimension, score, 'parent'),
        }
    
    # Render HTML template
    html_content = render_to_string('assessments/report.html', {
        'attempt': attempt,
        'dimension_reports': dimension_reports,
    })
    
    # Generate PDF
    pdf_file = HTML(string=html_content).write_pdf()
    
    # Save PDF to media
    filename = f"report_{attempt.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join('reports', filename)
    
    from django.core.files.base import ContentFile
    attempt.pdf_report_file.save(filepath, ContentFile(pdf_file), save=True)
    
    # Return PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# API endpoint for CSV upload (used by admin)
@api_view(['POST'])
def upload_csv(request):
    """API endpoint to upload CSV file for question import"""
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    
    try:
        from .services import import_questions_from_csv
        result = import_questions_from_csv(csv_file)
        return Response({
            'success': True,
            'created': result['created'],
            'updated': result['updated'],
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

