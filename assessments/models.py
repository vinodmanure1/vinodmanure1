from django.db import models


class Question(models.Model):
    """Model for assessment questions."""
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('creative', 'Creative'),
        ('analytical', 'Analytical'),
        ('social', 'Social'),
        ('practical', 'Practical'),
    ]
    
    text = models.TextField(help_text="The question text")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    weight = models.IntegerField(default=1, help_text="Weight of the question in scoring")
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.category}: {self.text[:50]}"


class StudentResponse(models.Model):
    """Model for student responses to assessment."""
    student_name = models.CharField(max_length=200)
    student_email = models.EmailField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Rating scale: 1 (Strongly Disagree) to 5 (Strongly Agree)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student_email', 'question']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.student_name} - {self.question.category}"


class CareerRecommendation(models.Model):
    """Model for storing career recommendations."""
    student_email = models.EmailField(unique=True)
    student_name = models.CharField(max_length=200)
    
    # Category scores
    technical_score = models.FloatField(default=0.0)
    creative_score = models.FloatField(default=0.0)
    analytical_score = models.FloatField(default=0.0)
    social_score = models.FloatField(default=0.0)
    practical_score = models.FloatField(default=0.0)
    
    # Top recommendation
    recommended_career = models.CharField(max_length=200)
    
    # Additional recommendations
    alternative_careers = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student_name} - {self.recommended_career}"
