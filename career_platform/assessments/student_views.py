from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Assessment, Question, Answer, Result
from .services import AssessmentScoringService


def home(request):
    """Display list of available assessments"""
    assessments = Assessment.objects.filter(is_active=True)
    context = {
        'assessments': assessments,
    }
    return render(request, 'assessments/home.html', context)


def take_assessment(request, assessment_id):
    """Display assessment form or process submission"""
    assessment = get_object_or_404(Assessment, id=assessment_id, is_active=True)
    questions = assessment.questions.prefetch_related('answers').all()
    
    if request.method == 'POST':
        # Collect responses
        responses = {}
        student_name = request.POST.get('student_name', '')
        student_email = request.POST.get('student_email', '')
        
        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                responses[str(question.id)] = int(answer_id)
        
        if not responses:
            messages.error(request, 'Please answer at least one question.')
            return redirect('take_assessment', assessment_id=assessment_id)
        
        # Create result
        user = request.user if request.user.is_authenticated else None
        result = AssessmentScoringService.create_result(
            assessment_id=assessment_id,
            responses=responses,
            user=user,
            student_name=student_name,
            student_email=student_email
        )
        
        return redirect('view_result', result_id=result.id)
    
    context = {
        'assessment': assessment,
        'questions': questions,
    }
    return render(request, 'assessments/take_assessment.html', context)


def view_result(request, result_id):
    """Display assessment result"""
    result = get_object_or_404(Result, id=result_id)
    
    # Sort careers by score
    sorted_scores = sorted(
        result.score_details.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    context = {
        'result': result,
        'sorted_scores': sorted_scores,
    }
    return render(request, 'assessments/result.html', context)


def download_pdf(request, result_id):
    """Generate and download PDF report"""
    result = get_object_or_404(Result, id=result_id)
    
    # Simple PDF generation placeholder
    # In production, use reportlab or weasyprint
    from io import BytesIO
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="assessment_result_{result.id}.pdf"'
    
    # Placeholder: Return text content as PDF simulation
    content = f"""
    Career Assessment Result
    ========================
    
    Assessment: {result.assessment.title}
    Date: {result.completed_at.strftime('%Y-%m-%d %H:%M')}
    Student: {result.student_name or (result.user.username if result.user else 'Anonymous')}
    
    Recommended Career: {result.recommended_career.name if result.recommended_career else 'N/A'}
    
    Career Scores:
    """
    
    for career_name, score in sorted(result.score_details.items(), key=lambda x: x[1], reverse=True):
        content += f"\n    {career_name}: {score}"
    
    content += "\n\n    Note: This is a simplified PDF. For production, use reportlab or weasyprint."
    
    response.write(content.encode('utf-8'))
    return response
