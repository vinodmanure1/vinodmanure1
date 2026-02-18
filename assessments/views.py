"""
API views for assessments app.
"""
import csv
import io
from datetime import datetime
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from weasyprint import HTML
from django.template.loader import render_to_string
from django.conf import settings
import os

from .models import Question, Test, Attempt, Profile
from .services import compute_scores, get_feedback_for_score


@csrf_exempt
@require_http_methods(["POST"])
def import_questions_csv(request):
    """
    Admin endpoint to import questions from uploaded CSV file.
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        # Read CSV
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created_count = 0
        for row in reader:
            question, created = Question.objects.get_or_create(
                question_text=row['question_text'],
                defaults={
                    'option_a': row['option_a'],
                    'option_b': row['option_b'],
                    'option_c': row['option_c'],
                    'option_d': row['option_d'],
                    'correct_answer': row['correct_answer'].upper(),
                    'category': row['category'],
                    'difficulty': row.get('difficulty', 'Medium'),
                }
            )
            if created:
                created_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Imported {created_count} new questions'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def submit_attempt(request):
    """
    Submit a test attempt and compute scores.
    
    Expected payload:
    {
        "test_id": 1,
        "student_name": "John Doe",
        "student_email": "john@example.com",
        "answers": {"1": "A", "2": "B", ...}
    }
    """
    try:
        data = request.data
        test_id = data.get('test_id')
        student_name = data.get('student_name')
        student_email = data.get('student_email', '')
        answers = data.get('answers', {})
        
        # Validate
        if not test_id or not student_name or not answers:
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get test
        try:
            test = Test.objects.get(id=test_id, is_active=True)
        except Test.DoesNotExist:
            return Response(
                {'error': 'Test not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Compute scores
        scores = compute_scores(test_id, answers)
        
        # Create attempt
        attempt = Attempt.objects.create(
            test=test,
            student_name=student_name,
            student_email=student_email,
            answers=answers,
            scores=scores,
            completed_at=datetime.now()
        )
        
        return Response({
            'success': True,
            'attempt_id': attempt.id,
            'scores': scores
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def generate_report_pdf(request, attempt_id):
    """
    Generate and return PDF report for an attempt.
    """
    try:
        attempt = Attempt.objects.select_related('test').get(id=attempt_id)
        
        # Check if PDF already exists
        if attempt.report_pdf:
            return FileResponse(
                attempt.report_pdf.open('rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=f'report_{attempt_id}.pdf'
            )
        
        # Generate feedback paragraphs
        feedback = {}
        if attempt.scores and 'category_scores' in attempt.scores:
            for category, score_data in attempt.scores['category_scores'].items():
                percentage = score_data['percentage']
                feedback[category] = get_feedback_for_score(category, percentage)
        
        # Render HTML
        html_content = render_to_string('assessments/report_template.html', {
            'attempt': attempt,
            'scores': attempt.scores,
            'feedback': feedback,
        })
        
        # Generate PDF
        pdf_file = HTML(string=html_content).write_pdf()
        
        # Save to attempt
        pdf_filename = f'report_{attempt_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        attempt.report_pdf.save(pdf_filename, ContentFile(pdf_file), save=True)
        
        # Return PDF
        return FileResponse(
            io.BytesIO(pdf_file),
            content_type='application/pdf',
            as_attachment=True,
            filename=pdf_filename
        )
    
    except Attempt.DoesNotExist:
        return Response(
            {'error': 'Attempt not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
