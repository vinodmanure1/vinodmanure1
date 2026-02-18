from collections import defaultdict
from django.db.models import Q
from .models import Assessment, Question, Answer, Result, Career


class AssessmentScoringService:
    """Service for scoring assessment responses and recommending careers"""
    
    @staticmethod
    def calculate_scores(assessment_id, responses):
        """
        Calculate career scores based on responses
        
        Args:
            assessment_id: ID of the assessment
            responses: dict mapping question_id to answer_id
            
        Returns:
            dict: career_id -> total_score mapping
        """
        career_scores = defaultdict(int)
        
        for question_id, answer_id in responses.items():
            try:
                answer = Answer.objects.select_related('career').get(
                    id=answer_id,
                    question_id=question_id
                )
                if answer.career:
                    career_scores[answer.career.id] += answer.score
            except Answer.DoesNotExist:
                continue
        
        return dict(career_scores)
    
    @staticmethod
    def get_recommended_career(career_scores):
        """
        Get the top recommended career based on scores
        
        Args:
            career_scores: dict mapping career_id to score
            
        Returns:
            Career: The recommended career object or None
        """
        if not career_scores:
            return None
        
        top_career_id = max(career_scores, key=career_scores.get)
        try:
            return Career.objects.get(id=top_career_id)
        except Career.DoesNotExist:
            return None
    
    @staticmethod
    def create_result(assessment_id, responses, user=None, student_name='', student_email=''):
        """
        Create an assessment result with calculated scores
        
        Args:
            assessment_id: ID of the assessment
            responses: dict mapping question_id to answer_id
            user: User object (optional)
            student_name: Name of student if not logged in
            student_email: Email of student if not logged in
            
        Returns:
            Result: The created result object
        """
        assessment = Assessment.objects.get(id=assessment_id)
        career_scores = AssessmentScoringService.calculate_scores(assessment_id, responses)
        recommended_career = AssessmentScoringService.get_recommended_career(career_scores)
        
        # Create detailed score report
        score_details = {}
        for career_id, score in career_scores.items():
            try:
                career = Career.objects.get(id=career_id)
                score_details[career.name] = score
            except Career.DoesNotExist:
                continue
        
        result = Result.objects.create(
            user=user,
            assessment=assessment,
            student_name=student_name,
            student_email=student_email,
            recommended_career=recommended_career,
            score_details=score_details,
            responses=responses
        )
        
        return result
