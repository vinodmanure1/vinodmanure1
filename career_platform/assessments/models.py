from django.db import models
from django.contrib.auth.models import User


class Career(models.Model):
    """Represents a career path or field"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    industry = models.CharField(max_length=200)
    average_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    growth_rate = models.FloatField(help_text="Expected growth rate as percentage", null=True, blank=True)
    education_required = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Assessment(models.Model):
    """Assessment containing multiple questions"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """Question in an assessment"""
    QUESTION_TYPES = [
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
        ('RATING', 'Rating Scale'),
        ('TEXT', 'Text Response'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='MULTIPLE_CHOICE')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['assessment', 'order']

    def __str__(self):
        return f"{self.assessment.title} - Q{self.order}: {self.text[:50]}"


class Answer(models.Model):
    """Possible answer for a question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    score = models.IntegerField(default=0, help_text="Score for this answer towards the career")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question', 'order']

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text[:30]}"


class Result(models.Model):
    """Student's assessment result"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_results', null=True, blank=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='results')
    student_name = models.CharField(max_length=200, blank=True)
    student_email = models.EmailField(blank=True)
    recommended_career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='results', null=True, blank=True)
    score_details = models.JSONField(default=dict, help_text="JSON containing scores for each career")
    responses = models.JSONField(default=dict, help_text="JSON containing question-answer pairs")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        user_display = self.student_name or (self.user.username if self.user else "Anonymous")
        return f"{user_display} - {self.assessment.title} - {self.completed_at.strftime('%Y-%m-%d')}"
