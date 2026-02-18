"""
Models for the Career Guidance Platform assessments app.
"""
from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Represents a single assessment question in the question bank.
    """
    question_text = models.TextField(help_text="The question text")
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        help_text="The correct answer option"
    )
    category = models.CharField(
        max_length=100,
        help_text="Category or skill area (e.g., Math, Verbal, Logical)"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')],
        default='Medium'
    )
    
    def __str__(self):
        return f"{self.category} - {self.question_text[:50]}"
    
    class Meta:
        ordering = ['category', 'difficulty']


class Test(models.Model):
    """
    Represents a test/assessment that can be taken by students.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class TestQuestion(models.Model):
    """
    Links questions to tests with ordering.
    """
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.test.title} - Q{self.order}"
    
    class Meta:
        ordering = ['test', 'order']
        unique_together = ['test', 'question']


class Profile(models.Model):
    """
    Extended user profile for students.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    school = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name


class Attempt(models.Model):
    """
    Represents a student's attempt at taking a test.
    """
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='attempts', null=True, blank=True)
    student_name = models.CharField(max_length=255, help_text="Student name for non-authenticated attempts")
    student_email = models.EmailField(blank=True)
    answers = models.JSONField(
        help_text="Dictionary mapping question_id to selected answer (A/B/C/D)"
    )
    scores = models.JSONField(
        help_text="Dictionary with category-wise scores and total",
        null=True,
        blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    report_pdf = models.FileField(upload_to='reports/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.student_name} - {self.test.title}"
    
    class Meta:
        ordering = ['-started_at']


class ReportParagraphMapping(models.Model):
    """
    Maps score ranges to report paragraph text for personalized feedback.
    """
    category = models.CharField(max_length=100, help_text="Skill category (e.g., Math, Verbal)")
    min_score = models.IntegerField(help_text="Minimum score percentage")
    max_score = models.IntegerField(help_text="Maximum score percentage")
    paragraph_text = models.TextField(help_text="Feedback text for this score range")
    
    def __str__(self):
        return f"{self.category}: {self.min_score}-{self.max_score}%"
    
    class Meta:
        ordering = ['category', 'min_score']
        unique_together = ['category', 'min_score', 'max_score']
