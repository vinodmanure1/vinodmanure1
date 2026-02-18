"""
Business logic for computing test scores and generating reports.
"""
from django.utils import timezone
from .models import Attempt, TestQuestion, ReportParagraphMapping


def compute_scores(attempt):
    """
    Compute deterministic scores for a test attempt.
    
    Args:
        attempt: Attempt instance
        
    Returns:
        dict: Updated scores dictionary with category-wise breakdown
    """
    if not attempt.answers:
        return {}
    
    # Get all questions for this test
    test_questions = TestQuestion.objects.filter(
        test=attempt.test
    ).select_related('question')
    
    # Initialize category scores
    category_scores = {}
    category_totals = {}
    
    # Calculate scores
    total_correct = 0
    total_questions = 0
    
    for tq in test_questions:
        question = tq.question
        category = question.category
        
        # Initialize category if not exists
        if category not in category_scores:
            category_scores[category] = 0
            category_totals[category] = 0
        
        # Check if answer is correct
        question_id = str(question.id)
        if question_id in attempt.answers:
            user_answer = attempt.answers[question_id]
            if user_answer == question.correct_answer:
                category_scores[category] += 1
                total_correct += 1
        
        category_totals[category] += 1
        total_questions += 1
    
    # Convert to percentages
    scores = {}
    for category in category_scores:
        if category_totals[category] > 0:
            percentage = (category_scores[category] / category_totals[category]) * 100
            scores[category] = {
                'correct': category_scores[category],
                'total': category_totals[category],
                'percentage': round(percentage, 2)
            }
    
    # Update attempt
    attempt.scores = scores
    attempt.total_score = total_correct
    if total_questions > 0:
        attempt.percentage = round((total_correct / total_questions) * 100, 2)
    else:
        attempt.percentage = 0.0
    
    attempt.status = 'completed'
    attempt.completed_at = timezone.now()
    attempt.save()
    
    return scores


def get_report_content(attempt):
    """
    Generate report content based on attempt scores.
    
    Args:
        attempt: Attempt instance with computed scores
        
    Returns:
        dict: Report content with paragraphs for each category
    """
    if not attempt.scores:
        compute_scores(attempt)
    
    report = {
        'attempt': attempt,
        'categories': []
    }
    
    for category, score_data in attempt.scores.items():
        percentage = score_data['percentage']
        
        # Find matching report paragraph
        mapping = ReportParagraphMapping.objects.filter(
            category=category,
            min_score__lte=percentage,
            max_score__gte=percentage
        ).first()
        
        category_report = {
            'name': category,
            'score': score_data['correct'],
            'total': score_data['total'],
            'percentage': percentage,
            'title': mapping.title if mapping else 'No guidance available',
            'content': mapping.content if mapping else '',
            'recommendations': mapping.recommendations if mapping else ''
        }
        
        report['categories'].append(category_report)
    
    return report
