from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Question(models.Model):
    """
    Represents an assessment question with predefined options.
    """
    CATEGORY_CHOICES = [
        ('technical', 'Technical Skills'),
        ('creative', 'Creative Skills'),
        ('analytical', 'Analytical Skills'),
        ('interpersonal', 'Interpersonal Skills'),
        ('leadership', 'Leadership Skills'),
    ]
    
    text = models.TextField(help_text="The question text")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category}: {self.text[:50]}"
    
    class Meta:
        ordering = ['category', 'created_at']


class Test(models.Model):
    """
    Represents a test consisting of multiple questions.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(180)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class TestQuestion(models.Model):
    """
    Links questions to tests with ordering.
    """
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.test.name} - Q{self.order}"
    
    class Meta:
        ordering = ['test', 'order']
        unique_together = ['test', 'question']


class Profile(models.Model):
    """
    User profile to store additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.user.username})"


class Attempt(models.Model):
    """
    Stores test attempt information and results.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Store answers as JSON: {"question_id": "selected_option"}
    answers = models.JSONField(default=dict)
    
    # Computed scores by category
    scores = models.JSONField(default=dict, help_text="Category-wise scores")
    total_score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.user.username} - {self.test.name} ({self.status})"
    
    class Meta:
        ordering = ['-started_at']


class ReportParagraphMapping(models.Model):
    """
    Maps score ranges to career guidance paragraphs.
    """
    category = models.CharField(max_length=50)
    min_score = models.IntegerField(validators=[MinValueValidator(0)])
    max_score = models.IntegerField(validators=[MinValueValidator(0)])
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Career guidance paragraph")
    recommendations = models.TextField(help_text="Specific recommendations")
    
    def __str__(self):
        return f"{self.category}: {self.min_score}-{self.max_score}"
    
    class Meta:
        ordering = ['category', 'min_score']
        unique_together = ['category', 'min_score', 'max_score']
