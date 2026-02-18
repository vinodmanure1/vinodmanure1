from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Test, Attempt, Profile
from .services import compute_scores, get_report_content


def index(request):
    """Landing page - redirect to dashboard if logged in."""
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    # Auto-login as demo user for MVP
    user, created = User.objects.get_or_create(username='demo_student')
    if created:
        user.set_password('demo123')
        user.save()
        Profile.objects.create(
            user=user,
            full_name='Demo Student',
            email='demo@example.com'
        )
    
    login(request, user)
    return redirect('student_dashboard')


@login_required
def student_dashboard(request):
    """Student dashboard showing available tests and past attempts."""
    tests = Test.objects.filter(is_active=True)
    attempts = Attempt.objects.filter(user=request.user).order_by('-started_at')[:10]
    
    context = {
        'tests': tests,
        'attempts': attempts
    }
    return render(request, 'assessments/student_dashboard.html', context)


@login_required
def take_test(request, test_id):
    """Take a test."""
    test = get_object_or_404(Test, id=test_id, is_active=True)
    
    if request.method == 'POST':
        # Create or get existing in-progress attempt
        attempt = Attempt.objects.filter(
            user=request.user,
            test=test,
            status='in_progress'
        ).first()
        
        if not attempt:
            attempt = Attempt.objects.create(
                user=request.user,
                test=test,
                status='in_progress'
            )
        
        # Process submitted answers
        answers = {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                answers[question_id] = value
        
        attempt.answers = answers
        attempt.save()
        
        # Compute scores
        compute_scores(attempt)
        
        return redirect('view_report', attempt_id=attempt.id)
    
    # Get questions for the test
    test_questions = test.test_questions.all().select_related('question')
    
    context = {
        'test': test,
        'test_questions': test_questions
    }
    return render(request, 'assessments/take_test.html', context)


@login_required
def view_report(request, attempt_id):
    """View test report."""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    # Ensure scores are computed
    if attempt.status != 'completed':
        compute_scores(attempt)
    
    # Get report content
    report_data = get_report_content(attempt)
    
    context = {
        'attempt': attempt,
        'report': report_data
    }
    return render(request, 'assessments/view_report.html', context)


@login_required
def download_pdf_report(request, attempt_id):
    """Generate and download PDF report."""
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    # Ensure scores are computed
    if attempt.status != 'completed':
        compute_scores(attempt)
    
    # Get report content
    report_data = get_report_content(attempt)
    
    # Render HTML template
    html_string = render_to_string('assessments/report.html', {
        'attempt': attempt,
        'report': report_data,
        'user': request.user
    })
    
    # Generate PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Return PDF response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="career_report_{attempt.id}.pdf"'
    
    return response
