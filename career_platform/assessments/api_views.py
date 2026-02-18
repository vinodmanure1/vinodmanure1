from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Assessment, Question, Answer, Result, Career
from .services import AssessmentScoringService


@require_http_methods(["GET"])
def list_assessments(request):
    """API endpoint to list all active assessments"""
    assessments = Assessment.objects.filter(is_active=True).values(
        'id', 'title', 'description', 'duration_minutes'
    )
    return JsonResponse({
        'status': 'success',
        'data': list(assessments)
    })


@require_http_methods(["GET"])
def get_assessment(request, assessment_id):
    """API endpoint to get assessment details with questions"""
    try:
        assessment = Assessment.objects.get(id=assessment_id, is_active=True)
        questions = []
        
        for question in assessment.questions.prefetch_related('answers').all():
            answers = [
                {
                    'id': answer.id,
                    'text': answer.text,
                    'order': answer.order
                }
                for answer in question.answers.all()
            ]
            
            questions.append({
                'id': question.id,
                'text': question.text,
                'question_type': question.question_type,
                'order': question.order,
                'answers': answers
            })
        
        data = {
            'id': assessment.id,
            'title': assessment.title,
            'description': assessment.description,
            'duration_minutes': assessment.duration_minutes,
            'questions': questions
        }
        
        return JsonResponse({
            'status': 'success',
            'data': data
        })
    except Assessment.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Assessment not found'
        }, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def submit_assessment(request):
    """API endpoint to submit assessment responses"""
    try:
        data = json.loads(request.body)
        assessment_id = data.get('assessment_id')
        responses = data.get('responses', {})
        student_name = data.get('student_name', '')
        student_email = data.get('student_email', '')
        
        if not assessment_id or not responses:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields: assessment_id and responses'
            }, status=400)
        
        # Create result
        user = request.user if request.user.is_authenticated else None
        result = AssessmentScoringService.create_result(
            assessment_id=assessment_id,
            responses=responses,
            user=user,
            student_name=student_name,
            student_email=student_email
        )
        
        response_data = {
            'id': result.id,
            'recommended_career': {
                'id': result.recommended_career.id,
                'name': result.recommended_career.name,
                'description': result.recommended_career.description,
            } if result.recommended_career else None,
            'score_details': result.score_details,
            'completed_at': result.completed_at.isoformat()
        }
        
        return JsonResponse({
            'status': 'success',
            'data': response_data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def list_results(request):
    """API endpoint to list assessment results"""
    results = Result.objects.select_related(
        'assessment', 'recommended_career', 'user'
    ).all()[:50]  # Limit to 50 recent results
    
    data = []
    for result in results:
        user_display = result.student_name or (result.user.username if result.user else 'Anonymous')
        data.append({
            'id': result.id,
            'user': user_display,
            'assessment': result.assessment.title,
            'recommended_career': result.recommended_career.name if result.recommended_career else None,
            'completed_at': result.completed_at.isoformat()
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })
