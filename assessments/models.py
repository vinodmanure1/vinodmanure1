from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    """Extended user profile with grade and role"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    grade = models.IntegerField(null=True, blank=True, help_text="Student grade level")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Question(models.Model):
    """Question bank for assessments"""
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('rating', 'Rating Scale'),
    ]
    
    DIMENSION_CHOICES = [
        ('aptitude', 'Aptitude'),
        ('logical', 'Logical Reasoning'),
        ('interest', 'Interest'),
        ('motivation', 'Motivation'),
    ]
    
    external_id = models.CharField(max_length=100, unique=True, help_text="External question ID")
    grade = models.IntegerField(help_text="Grade level")
    topic = models.CharField(max_length=200, help_text="Question topic/category")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    question_text = models.TextField(help_text="The question text")
    options = models.JSONField(help_text="Answer options as JSON", null=True, blank=True)
    correct_answer = models.CharField(max_length=200, help_text="Correct answer or key")
    weight = models.FloatField(default=1.0, help_text="Question weight for scoring")
    dimension = models.CharField(max_length=50, choices=DIMENSION_CHOICES, help_text="Assessment dimension")
    
    class Meta:
        ordering = ['external_id']
        
    def __str__(self):
        return f"{self.external_id} - {self.topic}"


class Test(models.Model):
    """Assessment test configuration"""
    name = models.CharField(max_length=200, help_text="Test name")
    grade = models.IntegerField(help_text="Grade level for this test")
    duration_minutes = models.IntegerField(help_text="Test duration in minutes")
    questions = models.ManyToManyField(Question, through='TestQuestion', related_name='tests')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - Grade {self.grade}"


class TestQuestion(models.Model):
    """Junction table for test-question relationship with ordering"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_questions')
    sequence = models.IntegerField(help_text="Question order in the test")
    
    class Meta:
        ordering = ['sequence']
        unique_together = ['test', 'question']
        
    def __str__(self):
        return f"{self.test.name} - Q{self.sequence}"


class Attempt(models.Model):
    """Student test attempt with results"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    raw_answers = models.JSONField(default=dict, help_text="Student answers as JSON")
    scores = models.JSONField(default=dict, help_text="Computed scores by dimension")
    total_score = models.FloatField(null=True, blank=True, help_text="Overall score")
    pdf_report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.test.name} - {self.started_at.date()}"
    
    @property
    def is_completed(self):
        return self.completed_at is not None


class ReportParagraphMapping(models.Model):
    """Mapping of score ranges to report paragraphs"""
    dimension = models.CharField(max_length=50, help_text="Assessment dimension")
    score_range = models.CharField(max_length=50, help_text="Score range (e.g., '0-30', '31-60', '61-100')")
    student_paragraph = models.TextField(help_text="Paragraph for student report")
    parent_paragraph = models.TextField(help_text="Paragraph for parent report")
    
    class Meta:
        ordering = ['dimension', 'score_range']
        unique_together = ['dimension', 'score_range']
        
    def __str__(self):
        return f"{self.dimension} - {self.score_range}"

