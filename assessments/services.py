"""
Business logic for assessment scoring and report generation.
"""
from typing import Dict, List
from .models import TestQuestion, ReportParagraphMapping


def compute_scores(test_id: int, answers: Dict[str, str]) -> Dict:
    """
    Compute scores for a test attempt using deterministic logic.
    
    Args:
        test_id: The ID of the test
        answers: Dictionary mapping question_id (as string) to answer choice (A/B/C/D)
    
    Returns:
        Dictionary containing:
        - category_scores: Dict mapping category name to dict with correct, total, percentage
        - total_score: Dict with correct, total, percentage for overall test
    """
    # Get all test questions for this test
    test_questions = TestQuestion.objects.filter(
        test_id=test_id
    ).select_related('question')
    
    # Initialize category tracking
    category_stats = {}
    total_correct = 0
    total_questions = 0
    
    # Process each question
    for tq in test_questions:
        question = tq.question
        question_id = str(question.id)
        category = question.category
        
        # Initialize category if not seen before
        if category not in category_stats:
            category_stats[category] = {'correct': 0, 'total': 0}
        
        # Check if answer is correct
        student_answer = answers.get(question_id, '')
        is_correct = (student_answer.upper() == question.correct_answer.upper())
        
        # Update stats
        category_stats[category]['total'] += 1
        total_questions += 1
        
        if is_correct:
            category_stats[category]['correct'] += 1
            total_correct += 1
    
    # Calculate percentages
    category_scores = {}
    for category, stats in category_stats.items():
        if stats['total'] > 0:
            percentage = round((stats['correct'] / stats['total']) * 100, 2)
        else:
            percentage = 0.0
        
        category_scores[category] = {
            'correct': stats['correct'],
            'total': stats['total'],
            'percentage': percentage
        }
    
    # Calculate total score
    if total_questions > 0:
        total_percentage = round((total_correct / total_questions) * 100, 2)
    else:
        total_percentage = 0.0
    
    return {
        'category_scores': category_scores,
        'total_score': {
            'correct': total_correct,
            'total': total_questions,
            'percentage': total_percentage
        }
    }


def get_feedback_for_score(category: str, percentage: float) -> str:
    """
    Get personalized feedback paragraph based on score percentage.
    
    Args:
        category: The skill category
        percentage: The score percentage (0-100)
    
    Returns:
        Feedback text or default message if no mapping found
    """
    try:
        mapping = ReportParagraphMapping.objects.filter(
            category=category,
            min_score__lte=percentage,
            max_score__gte=percentage
        ).first()
        
        if mapping:
            return mapping.paragraph_text
        else:
            return f"Your performance in {category} shows room for growth. Keep practicing!"
    except Exception:
        return f"Score: {percentage}% in {category}"
