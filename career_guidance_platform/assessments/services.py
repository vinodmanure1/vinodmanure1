"""
Scoring engine for career guidance assessments.
"""
from collections import defaultdict
from typing import Dict, List, Tuple


def compute_scores(attempt_answers: Dict[int, float], test) -> Dict:
    """
    Compute normalized scores per dimension and identify top dimensions.
    
    Args:
        attempt_answers: Dictionary mapping question_id to answer value (0-10 scale)
        test: Test object containing questions
    
    Returns:
        Dictionary containing:
            - dimension_scores: Dict of dimension -> normalized score (0-100)
            - total_score: Overall average score (0-100)
            - top_dimensions: List of (dimension, score) tuples sorted by score
    """
    # Collect scores by dimension
    dimension_raw_scores = defaultdict(list)
    dimension_weights = defaultdict(list)
    
    # Get all test questions
    test_questions = test.test_questions.select_related('question').all()
    
    for tq in test_questions:
        question = tq.question
        question_id = question.id
        
        # Get the answer (default to 0 if not answered)
        answer_value = attempt_answers.get(str(question_id), 0)
        
        # Store raw score and weight
        dimension_raw_scores[question.dimension].append(answer_value)
        dimension_weights[question.dimension].append(question.weight)
    
    # Calculate weighted average for each dimension
    dimension_scores = {}
    for dimension, scores in dimension_raw_scores.items():
        weights = dimension_weights[dimension]
        
        # Calculate weighted average
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        if total_weight > 0:
            # Normalize to 0-100 scale (assuming answers are 0-10)
            avg_score = weighted_sum / total_weight
            normalized_score = (avg_score / 10.0) * 100.0
            dimension_scores[dimension] = round(normalized_score, 2)
        else:
            dimension_scores[dimension] = 0.0
    
    # Calculate total score as average of all dimension scores
    if dimension_scores:
        total_score = round(sum(dimension_scores.values()) / len(dimension_scores), 2)
    else:
        total_score = 0.0
    
    # Get top dimensions sorted by score
    top_dimensions = sorted(
        dimension_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return {
        'dimension_scores': dimension_scores,
        'total_score': total_score,
        'top_dimensions': top_dimensions
    }
