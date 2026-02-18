"""
Career scoring and recommendation service.
"""
from collections import defaultdict
from .models import StudentResponse, CareerRecommendation


class CareerScoringService:
    """Service for calculating career scores and recommendations."""
    
    # Career mapping based on dominant category
    CAREER_RECOMMENDATIONS = {
        'technical': [
            'Software Developer',
            'Data Scientist',
            'Systems Engineer',
            'Network Administrator',
            'Cybersecurity Analyst',
        ],
        'creative': [
            'Graphic Designer',
            'Content Creator',
            'Marketing Specialist',
            'UX/UI Designer',
            'Art Director',
        ],
        'analytical': [
            'Business Analyst',
            'Financial Analyst',
            'Research Scientist',
            'Data Analyst',
            'Management Consultant',
        ],
        'social': [
            'Human Resources Manager',
            'Social Worker',
            'Teacher',
            'Counselor',
            'Public Relations Specialist',
        ],
        'practical': [
            'Project Manager',
            'Operations Manager',
            'Civil Engineer',
            'Healthcare Administrator',
            'Supply Chain Manager',
        ],
    }
    
    @staticmethod
    def calculate_scores(student_email):
        """
        Calculate category scores for a student based on their responses.
        
        Args:
            student_email: Email of the student
            
        Returns:
            dict: Category scores normalized to 0-100 scale
        """
        responses = StudentResponse.objects.filter(student_email=student_email).select_related('question')
        
        if not responses.exists():
            return {}
        
        # Calculate weighted scores per category
        category_scores = defaultdict(lambda: {'total': 0, 'weight': 0})
        
        for response in responses:
            category = response.question.category
            weight = response.question.weight
            category_scores[category]['total'] += response.rating * weight
            category_scores[category]['weight'] += weight
        
        # Normalize scores to 0-100 scale (rating is 1-5, so max is 5)
        normalized_scores = {}
        for category, data in category_scores.items():
            if data['weight'] > 0:
                avg_score = data['total'] / data['weight']
                normalized_scores[category] = round((avg_score / 5.0) * 100, 2)
            else:
                normalized_scores[category] = 0.0
        
        return normalized_scores
    
    @classmethod
    def get_career_recommendations(cls, scores):
        """
        Get career recommendations based on category scores.
        
        Args:
            scores: dict of category scores
            
        Returns:
            tuple: (primary_career, alternative_careers)
        """
        if not scores:
            return "Complete assessment for recommendation", []
        
        # Sort categories by score
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get recommendations for top categories
        primary_category = sorted_categories[0][0]
        primary_career = cls.CAREER_RECOMMENDATIONS.get(primary_category, ['General Professional'])[0]
        
        # Get alternative careers from top 2-3 categories
        alternative_careers = []
        for category, score in sorted_categories[:3]:
            careers = cls.CAREER_RECOMMENDATIONS.get(category, [])
            for career in careers[1:3]:  # Get 2 alternatives per category
                if career not in alternative_careers and career != primary_career:
                    alternative_careers.append(career)
        
        return primary_career, alternative_careers[:4]  # Limit to 4 alternatives
    
    @classmethod
    def create_or_update_recommendation(cls, student_email, student_name):
        """
        Create or update career recommendation for a student.
        
        Args:
            student_email: Email of the student
            student_name: Name of the student
            
        Returns:
            CareerRecommendation: The created or updated recommendation
        """
        scores = cls.calculate_scores(student_email)
        
        if not scores:
            return None
        
        primary_career, alternative_careers = cls.get_career_recommendations(scores)
        
        recommendation, created = CareerRecommendation.objects.update_or_create(
            student_email=student_email,
            defaults={
                'student_name': student_name,
                'technical_score': scores.get('technical', 0.0),
                'creative_score': scores.get('creative', 0.0),
                'analytical_score': scores.get('analytical', 0.0),
                'social_score': scores.get('social', 0.0),
                'practical_score': scores.get('practical', 0.0),
                'recommended_career': primary_career,
                'alternative_careers': alternative_careers,
            }
        )
        
        return recommendation
