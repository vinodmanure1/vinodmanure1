from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Question(models.Model):
    """
    Question model representing assessment questions.
    """
    DIMENSION_CHOICES = [
        ('analytical', 'Analytical Thinking'),
        ('creative', 'Creative Thinking'),
        ('practical', 'Practical Skills'),
        ('social', 'Social Skills'),
        ('leadership', 'Leadership'),
        ('technical', 'Technical Skills'),
    ]
    
    text = models.TextField(help_text="Question text")
    dimension = models.CharField(max_length=50, choices=DIMENSION_CHOICES, 
                                 help_text="Skill dimension this question assesses")
    weight = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)],
                                 help_text="Weight of this question (1-10)")
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Q{self.id}: {self.text[:50]}"


class Test(models.Model):
    """
    Test model representing a collection of questions.
    """
    title = models.CharField(max_length=200, help_text="Test title")
    description = models.TextField(help_text="Test description")
    duration_minutes = models.IntegerField(default=30, help_text="Test duration in minutes")
    questions = models.ManyToManyField(Question, through='TestQuestion', related_name='tests')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class TestQuestion(models.Model):
    """
    Through model for Test-Question relationship with ordering.
    """
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, help_text="Question order in this test")
    
    class Meta:
        ordering = ['order']
        unique_together = ['test', 'question']
    
    def __str__(self):
        return f"{self.test.title} - Q{self.question.id}"


class Profile(models.Model):
    """
    User profile with additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=50, blank=True, help_text="Student grade/class")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile: {self.user.username}"


class Attempt(models.Model):
    """
    Test attempt by a user with scores and results.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    answers = models.JSONField(default=dict, help_text="Question ID to answer mapping")
    scores = models.JSONField(default=dict, help_text="Dimension scores and analytics")
    total_score = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    pdf_report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.status}"


class ReportParagraphMapping(models.Model):
    """
    Mapping of score ranges to report paragraphs for each dimension.
    """
    dimension = models.CharField(max_length=50, help_text="Skill dimension")
    score_min = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    score_max = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    student_paragraph = models.TextField(help_text="Paragraph for student report")
    parent_paragraph = models.TextField(help_text="Paragraph for parent report")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['dimension', 'score_min']
    
    def __str__(self):
        return f"{self.dimension}: {self.score_min}-{self.score_max}"

