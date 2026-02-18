import io
import os
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from .models import Test, Attempt, Question, TestQuestion
from .services import compute_scores
from .utils import import_questions_from_csv


def home(request):
    """Home page"""
    return render(request, 'assessments/home.html')


@login_required
def student_dashboard(request):
    """Student dashboard showing available tests and past attempts"""
    tests = Test.objects.filter(is_active=True)
    attempts = Attempt.objects.filter(user=request.user).select_related('test')
    
    context = {
        'tests': tests,
        'attempts': attempts
    }
    return render(request, 'assessments/dashboard.html', context)


@login_required
def take_test(request, test_id):
    """Take test page with questions and timer"""
    test = get_object_or_404(Test, id=test_id, is_active=True)
    test_questions = test.test_questions.select_related('question').order_by('order')
    
    # Create a new attempt
    attempt = Attempt.objects.create(
        user=request.user,
        test=test
    )
    
    context = {
        'test': test,
        'test_questions': test_questions,
        'attempt': attempt,
    }
    return render(request, 'assessments/take_test.html', context)


@login_required
@require_http_methods(["POST"])
def save_progress(request, attempt_id):
    """AJAX endpoint to autosave answers"""
    import json
    
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        # Update attempt answers
        attempt.answers = answers
        attempt.save()
        
        return JsonResponse({'status': 'success', 'message': 'Progress saved'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def submit_attempt(request, attempt_id):
    """Submit attempt and compute scores"""
    import json
    
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        # Update answers
        attempt.answers = answers
        
        # Compute scores
        score_result = compute_scores(answers, attempt.test)
        
        # Save scores
        attempt.scores = score_result['dimension_scores']
        attempt.total_score = score_result['total_score']
        attempt.top_dimensions = score_result['top_dimensions']
        attempt.completed_at = timezone.now()
        attempt.save()
        
        return JsonResponse({
            'status': 'success',
            'scores': score_result,
            'attempt_id': attempt.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def view_report(request, attempt_id):
    """View attempt report as HTML"""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    context = {
        'attempt': attempt,
        'user': request.user,
        'dimension_scores': attempt.scores,
        'total_score': attempt.total_score,
        'top_dimensions': attempt.top_dimensions[:3] if attempt.top_dimensions else []
    }
    
    return render(request, 'assessments/report.html', context)


@login_required
def download_pdf_report(request, attempt_id):
    """Generate and download PDF report"""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    # Check if PDF already exists
    if attempt.pdf_report_file:
        return FileResponse(
            attempt.pdf_report_file.open('rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f'report_{attempt.id}.pdf'
        )
    
    # Generate PDF
    context = {
        'attempt': attempt,
        'user': request.user,
        'dimension_scores': attempt.scores,
        'total_score': attempt.total_score,
        'top_dimensions': attempt.top_dimensions[:3] if attempt.top_dimensions else []
    }
    
    # Render HTML
    html_string = render(request, 'assessments/report.html', context).content.decode('utf-8')
    
    # Generate PDF
    font_config = FontConfiguration()
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf(font_config=font_config)
    
    # Save PDF to attempt
    filename = f'report_{attempt.id}_{attempt.user.username}.pdf'
    attempt.pdf_report_file.save(filename, ContentFile(pdf_file), save=True)
    
    # Return PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# Admin API Views
@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_upload_csv(request):
    """Admin API endpoint to upload CSV of questions"""
    try:
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import questions
        result = import_questions_from_csv(csv_file)
        
        return Response({
            'message': f'Successfully imported {result["created"]} questions',
            'created': result['created'],
            'errors': result['errors']
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
