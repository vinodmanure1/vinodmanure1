from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from .models import Question, StudentResponse, CareerRecommendation
from .services import CareerScoringService
from weasyprint import HTML
from django.template.loader import render_to_string


class AssessmentView(View):
    """View for taking the career assessment."""
    
    def get(self, request):
        """Display the assessment form."""
        questions = Question.objects.all()
        return render(request, 'assessments/assessment.html', {
            'questions': questions,
        })
    
    def post(self, request):
        """Process assessment submission."""
        student_name = request.POST.get('student_name')
        student_email = request.POST.get('student_email')
        
        if not student_name or not student_email:
            messages.error(request, 'Please provide your name and email.')
            return redirect('assessment')
        
        # Delete existing responses for this student
        StudentResponse.objects.filter(student_email=student_email).delete()
        
        # Save new responses
        questions = Question.objects.all()
        for question in questions:
            rating = request.POST.get(f'question_{question.id}')
            if rating:
                StudentResponse.objects.create(
                    student_name=student_name,
                    student_email=student_email,
                    question=question,
                    rating=int(rating)
                )
        
        # Generate recommendation
        CareerScoringService.create_or_update_recommendation(student_email, student_name)
        
        messages.success(request, 'Assessment completed successfully!')
        return redirect('results', email=student_email)


class ResultsView(View):
    """View for displaying assessment results."""
    
    def get(self, request, email):
        """Display results for a student."""
        recommendation = get_object_or_404(CareerRecommendation, student_email=email)
        
        scores = {
            'Technical': recommendation.technical_score,
            'Creative': recommendation.creative_score,
            'Analytical': recommendation.analytical_score,
            'Social': recommendation.social_score,
            'Practical': recommendation.practical_score,
        }
        
        return render(request, 'assessments/results.html', {
            'recommendation': recommendation,
            'scores': scores,
        })


class PDFReportView(View):
    """View for generating PDF report."""
    
    def get(self, request, email):
        """Generate and return PDF report."""
        recommendation = get_object_or_404(CareerRecommendation, student_email=email)
        
        scores = {
            'Technical': recommendation.technical_score,
            'Creative': recommendation.creative_score,
            'Analytical': recommendation.analytical_score,
            'Social': recommendation.social_score,
            'Practical': recommendation.practical_score,
        }
        
        # Render HTML template
        html_string = render_to_string('assessments/report_pdf.html', {
            'recommendation': recommendation,
            'scores': scores,
        })
        
        # Generate PDF
        pdf_file = HTML(string=html_string).write_pdf()
        
        # Sanitize filename to prevent security issues
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', recommendation.student_name)
        
        # Return PDF response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="career_report_{safe_name}.pdf"'
        
        return response


def home(request):
    """Home page view."""
    return render(request, 'assessments/home.html')
