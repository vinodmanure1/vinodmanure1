from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import csv
import io
import os
from datetime import datetime

from .models import Question, Test, Attempt, Profile, TestQuestion
from .serializers import (
    QuestionSerializer, TestSerializer, AttemptSerializer, 
    AttemptSubmitSerializer, ProfileSerializer
)
from .services import compute_scores


# Student Views (Server-rendered)
@login_required
def student_dashboard(request):
    """Student dashboard showing available tests and past attempts."""
    tests = Test.objects.filter(is_active=True)
    attempts = Attempt.objects.filter(user=request.user).select_related('test')
    
    context = {
        'tests': tests,
        'attempts': attempts,
    }
    return render(request, 'assessments/student_dashboard.html', context)


@login_required
def take_test(request, test_id):
    """Take test page with timer and questions."""
    test = get_object_or_404(Test, id=test_id, is_active=True)
    
    # Get or create an in-progress attempt
    attempt, created = Attempt.objects.get_or_create(
        user=request.user,
        test=test,
        status='in_progress',
        defaults={'answers': {}}
    )
    
    # Get questions for this test in order
    test_questions = TestQuestion.objects.filter(test=test).select_related('question').order_by('order')
    questions = [tq.question for tq in test_questions]
    
    context = {
        'test': test,
        'attempt': attempt,
        'questions': questions,
    }
    return render(request, 'assessments/take_test.html', context)


@login_required
@require_http_methods(["POST"])
def autosave_attempt(request, attempt_id):
    """Autosave endpoint for saving progress during test."""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    if attempt.status != 'in_progress':
        return JsonResponse({'error': 'Attempt is not in progress'}, status=400)
    
    import json
    data = json.loads(request.body)
    answers = data.get('answers', {})
    
    # Update answers
    attempt.answers = answers
    attempt.save()
    
    return JsonResponse({'success': True, 'saved_at': timezone.now().isoformat()})


@login_required
def view_report(request, attempt_id):
    """View attempt report."""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    if attempt.status != 'completed':
        return redirect('student_dashboard')
    
    context = {
        'attempt': attempt,
    }
    return render(request, 'assessments/report.html', context)


# API Views
class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for tests."""
    queryset = Test.objects.filter(is_active=True)
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]


class AttemptViewSet(viewsets.ModelViewSet):
    """API endpoint for attempts."""
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Attempt.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_attempt(request):
    """Submit attempt and compute scores."""
    serializer = AttemptSubmitSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    test_id = serializer.validated_data['test_id']
    answers = serializer.validated_data['answers']
    
    # Convert string keys to integers
    answers = {int(k): v for k, v in answers.items()}
    
    test = get_object_or_404(Test, id=test_id)
    
    # Find or create attempt
    attempt = Attempt.objects.filter(
        user=request.user,
        test=test,
        status='in_progress'
    ).first()
    
    if not attempt:
        attempt = Attempt.objects.create(
            user=request.user,
            test=test,
            status='in_progress',
            answers=answers
        )
    else:
        attempt.answers = answers
    
    # Compute scores
    scores_data = compute_scores(answers)
    attempt.scores = scores_data
    attempt.total_score = scores_data['total_score']
    attempt.status = 'completed'
    attempt.completed_at = timezone.now()
    attempt.save()
    
    return Response({
        'attempt_id': attempt.id,
        'scores': scores_data,
        'total_score': attempt.total_score,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def csv_upload(request):
    """Admin API endpoint for CSV upload."""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    try:
        # Read CSV file
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created_count = 0
        for row in reader:
            Question.objects.create(
                text=row.get('text', ''),
                dimension=row.get('dimension', 'analytical'),
                weight=int(row.get('weight', 1)),
                order=int(row.get('order', 0)),
                is_active=row.get('is_active', 'True').lower() == 'true'
            )
            created_count += 1
        
        return Response({
            'success': True,
            'created_count': created_count
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request, attempt_id):
    """Generate and return PDF report for an attempt."""
    attempt = get_object_or_404(Attempt, id=attempt_id)
    
    # Check permission
    if attempt.user != request.user and not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if PDF already exists
    if attempt.pdf_report_file:
        return FileResponse(attempt.pdf_report_file.open('rb'), content_type='application/pdf')
    
    # Generate PDF using WeasyPrint
    from django.template.loader import render_to_string
    from weasyprint import HTML
    
    html_string = render_to_string('assessments/report.html', {'attempt': attempt})
    
    # Create media directory if it doesn't exist
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reports'), exist_ok=True)
    
    # Generate PDF
    pdf_filename = f'report_{attempt.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'reports', pdf_filename)
    
    HTML(string=html_string).write_pdf(pdf_path)
    
    # Save PDF path to attempt
    attempt.pdf_report_file = f'reports/{pdf_filename}'
    attempt.save()
    
    # Use context manager for file handling
    with open(pdf_path, 'rb') as pdf_file:
        response = FileResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="report_{attempt.id}.pdf"'
        return response

