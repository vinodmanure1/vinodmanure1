"""
Scoring engine for computing assessment scores.
"""
from collections import defaultdict
from typing import Dict, List, Tuple
from .models import Question


def compute_scores(attempt_answers: Dict[int, int]) -> Dict:
    """
    Compute normalized scores for an attempt.
    
    Args:
        attempt_answers: Dictionary mapping question_id to answer score (0-5 scale)
    
    Returns:
        Dictionary containing:
        - dimension_scores: Dict of dimension to normalized score (0-100)
        - total_score: Overall normalized score
        - top_dimensions: List of top 3 dimensions
        - raw_scores: Raw scores before normalization
    """
    if not attempt_answers:
        return {
            'dimension_scores': {},
            'total_score': 0.0,
            'top_dimensions': [],
            'raw_scores': {}
        }
    
    # Get all questions that were answered
    question_ids = list(attempt_answers.keys())
    questions = Question.objects.filter(id__in=question_ids, is_active=True)
    
    # Calculate raw scores per dimension
    dimension_raw_scores = defaultdict(float)
    dimension_max_scores = defaultdict(float)
    
    for question in questions:
        answer_value = attempt_answers.get(question.id, 0)
        # Answer value is expected to be 0-5, weight is 1-10
        weighted_score = answer_value * question.weight
        max_possible = 5 * question.weight  # Maximum score for this question
        
        dimension_raw_scores[question.dimension] += weighted_score
        dimension_max_scores[question.dimension] += max_possible
    
    # Normalize scores to 0-100 scale
    dimension_scores = {}
    for dimension in dimension_raw_scores:
        if dimension_max_scores[dimension] > 0:
            normalized = (dimension_raw_scores[dimension] / dimension_max_scores[dimension]) * 100
            dimension_scores[dimension] = round(normalized, 2)
        else:
            dimension_scores[dimension] = 0.0
    
    # Calculate total score (average of all dimension scores)
    total_score = round(sum(dimension_scores.values()) / len(dimension_scores), 2) if dimension_scores else 0.0
    
    # Get top 3 dimensions
    sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
    top_dimensions = [dim for dim, score in sorted_dimensions[:3]]
    
    return {
        'dimension_scores': dimension_scores,
        'total_score': total_score,
        'top_dimensions': top_dimensions,
        'raw_scores': dict(dimension_raw_scores)
    }


def get_report_paragraphs(dimension: str, score: float) -> Tuple[str, str]:
    """
    Get report paragraphs for a dimension and score.
    
    Args:
        dimension: Dimension name
        score: Normalized score (0-100)
    
    Returns:
        Tuple of (student_paragraph, parent_paragraph)
    """
    from .models import ReportParagraphMapping
    
    try:
        mapping = ReportParagraphMapping.objects.filter(
            dimension=dimension,
            score_min__lte=score,
            score_max__gte=score
        ).first()
        
        if mapping:
            return mapping.student_paragraph, mapping.parent_paragraph
    except Exception:
        pass
    
    # Default paragraphs if no mapping found
    return (
        f"Your score in {dimension} is {score:.1f}/100.",
        f"Student scored {score:.1f}/100 in {dimension}."
    )
