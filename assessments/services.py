"""
Service for computing assessment scores.
"""
from typing import Dict, List, Tuple
from collections import defaultdict
from .models import Question, TestQuestion


def compute_scores(attempt_answers: Dict[int, int]) -> Dict:
    """
    Compute scores for an attempt based on answers.
    
    Args:
        attempt_answers: Dictionary mapping question_id to answer_value (1-5 scale)
        
    Returns:
        Dictionary containing:
        - dimension_scores: Dict[str, float] - normalized scores per dimension (0-100)
        - total_score: float - overall score (0-100)
        - top_dimensions: List[str] - top 3 dimensions by score
    """
    if not attempt_answers:
        return {
            'dimension_scores': {},
            'total_score': 0.0,
            'top_dimensions': []
        }
    
    # Get all questions that were answered
    question_ids = list(attempt_answers.keys())
    questions = Question.objects.filter(id__in=question_ids)
    
    # Group by dimension and calculate weighted scores
    dimension_data = defaultdict(lambda: {'total': 0.0, 'max_possible': 0.0})
    
    for question in questions:
        answer_value = attempt_answers.get(question.id, 0)
        dimension = question.dimension
        weight = question.weight
        
        # Assuming answer scale is 1-5, normalize to 0-1 then apply weight
        # Answer value of 5 = perfect score for this question
        normalized_answer = (answer_value - 1) / 4.0 if answer_value >= 1 else 0.0
        weighted_score = normalized_answer * weight
        
        dimension_data[dimension]['total'] += weighted_score
        dimension_data[dimension]['max_possible'] += weight
    
    # Calculate normalized dimension scores (0-100)
    dimension_scores = {}
    for dimension, data in dimension_data.items():
        if data['max_possible'] > 0:
            # Normalize to 0-100 scale
            dimension_scores[dimension] = round((data['total'] / data['max_possible']) * 100, 2)
        else:
            dimension_scores[dimension] = 0.0
    
    # Calculate total score as average of all dimension scores
    if dimension_scores:
        total_score = round(sum(dimension_scores.values()) / len(dimension_scores), 2)
    else:
        total_score = 0.0
    
    # Get top 3 dimensions
    sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
    top_dimensions = [dim for dim, score in sorted_dimensions[:3]]
    
    return {
        'dimension_scores': dimension_scores,
        'total_score': total_score,
        'top_dimensions': top_dimensions
    }
