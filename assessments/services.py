"""
Business logic for assessments including scoring and CSV import
"""
import csv
import io
from typing import Dict, List, Any
from django.db import transaction
from .models import Question, TestQuestion, Attempt


def import_questions_from_csv(csv_file) -> Dict[str, int]:
    """
    Import questions from CSV file
    Expected columns: external_id, grade, topic, question_type, question_text, 
                     options, correct_answer, weight, dimension
    Returns dict with counts of created and updated questions
    """
    created_count = 0
    updated_count = 0
    
    # Read CSV content
    if hasattr(csv_file, 'read'):
        content = csv_file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
    else:
        content = csv_file
    
    csv_reader = csv.DictReader(io.StringIO(content))
    
    with transaction.atomic():
        for row in csv_reader:
            external_id = row.get('external_id', '').strip()
            if not external_id:
                continue
            
            # Parse options from CSV (can be JSON string or comma-separated)
            options_str = row.get('options', '')
            if options_str:
                try:
                    import json
                    options = json.loads(options_str)
                except:
                    # If not JSON, treat as comma-separated list
                    options = [opt.strip() for opt in options_str.split(',')]
            else:
                options = []
            
            question_data = {
                'grade': int(row.get('grade', 9)),
                'topic': row.get('topic', 'General'),
                'question_type': row.get('question_type', 'mcq'),
                'question_text': row.get('question_text', ''),
                'options': options,
                'correct_answer': row.get('correct_answer', ''),
                'weight': float(row.get('weight', 1.0)),
                'dimension': row.get('dimension', 'aptitude'),
            }
            
            # Create or update question
            question, created = Question.objects.update_or_create(
                external_id=external_id,
                defaults=question_data
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
    
    return {'created': created_count, 'updated': updated_count}


def compute_scores(attempt: Attempt) -> Dict[str, Any]:
    """
    Compute deterministic scores for an attempt based on answers
    Returns dict with dimension scores, total score, and top dimensions
    """
    raw_answers = attempt.raw_answers
    test_questions = TestQuestion.objects.filter(test=attempt.test).select_related('question')
    
    # Initialize dimension scores
    dimension_scores = {}
    dimension_weights = {}
    
    for tq in test_questions:
        question = tq.question
        dimension = question.dimension
        
        # Initialize dimension if not exists
        if dimension not in dimension_scores:
            dimension_scores[dimension] = 0
            dimension_weights[dimension] = 0
        
        # Get user's answer
        question_id = str(question.id)
        user_answer = raw_answers.get(question_id, '')
        
        # Calculate score for this question
        if user_answer:
            # For MCQ and True/False, check if answer is correct
            if question.question_type in ['mcq', 'true_false']:
                is_correct = str(user_answer).strip().lower() == str(question.correct_answer).strip().lower()
                question_score = question.weight if is_correct else 0
            else:
                # For rating scales, normalize the answer (assuming 1-5 scale)
                try:
                    rating = int(user_answer)
                    question_score = (rating / 5.0) * question.weight
                except:
                    question_score = 0
            
            dimension_scores[dimension] += question_score
        
        dimension_weights[dimension] += question.weight
    
    # Normalize scores to 0-100 scale for each dimension
    normalized_scores = {}
    for dimension, score in dimension_scores.items():
        max_score = dimension_weights[dimension]
        if max_score > 0:
            normalized_scores[dimension] = round((score / max_score) * 100, 2)
        else:
            normalized_scores[dimension] = 0
    
    # Calculate total score (average of all dimensions)
    if normalized_scores:
        total_score = round(sum(normalized_scores.values()) / len(normalized_scores), 2)
    else:
        total_score = 0
    
    # Identify top 3 dimensions
    sorted_dimensions = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
    top_dimensions = [dim for dim, score in sorted_dimensions[:3]]
    
    return {
        'dimension_scores': normalized_scores,
        'total_score': total_score,
        'top_dimensions': top_dimensions,
    }


def get_report_paragraph(dimension: str, score: float, recipient: str = 'student') -> str:
    """
    Get the appropriate report paragraph for a dimension and score
    recipient: 'student' or 'parent'
    """
    from .models import ReportParagraphMapping
    
    # Determine score range
    if score <= 30:
        score_range = '0-30'
    elif score <= 60:
        score_range = '31-60'
    else:
        score_range = '61-100'
    
    try:
        mapping = ReportParagraphMapping.objects.get(dimension=dimension, score_range=score_range)
        return mapping.student_paragraph if recipient == 'student' else mapping.parent_paragraph
    except ReportParagraphMapping.DoesNotExist:
        return f"Score in {dimension}: {score}/100"
