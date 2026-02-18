from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Question(models.Model):
    """Model for storing assessment questions."""
    DIMENSION_CHOICES = [
        ('technical', 'Technical Skills'),
        ('creative', 'Creative Thinking'),
        ('analytical', 'Analytical Skills'),
        ('leadership', 'Leadership'),
        ('communication', 'Communication'),
    ]
    
    text = models.TextField(help_text="The question text")
    dimension = models.CharField(max_length=50, choices=DIMENSION_CHOICES, 
                                help_text="Career dimension this question assesses")
    weight = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)],
                              help_text="Weight of this question in scoring")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['dimension', 'id']
    
    def __str__(self):
        return f"{self.dimension}: {self.text[:50]}..."


class Test(models.Model):
    """Model for assessment tests."""
    name = models.CharField(max_length=200, help_text="Name of the test")
    description = models.TextField(help_text="Description of the test")
    duration_minutes = models.IntegerField(default=30, 
                                          validators=[MinValueValidator(1)],
                                          help_text="Duration in minutes")
    is_active = models.BooleanField(default=True, help_text="Is this test active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class TestQuestion(models.Model):
    """Model for the many-to-many relationship between Test and Question."""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_questions')
    order = models.IntegerField(default=0, help_text="Order of question in the test")
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['test', 'question']
    
    def __str__(self):
        return f"{self.test.name} - Q{self.order}"


class Profile(models.Model):
    """User profile model with OneToOne relationship to User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile: {self.user.username}"


class Attempt(models.Model):
    """Model for storing user test attempts."""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Store answers as JSON: {question_id: answer_value}
    answers = models.JSONField(default=dict, blank=True)
    
    # Store computed scores
    dimension_scores = models.JSONField(default=dict, blank=True, 
                                       help_text="Scores per dimension (0-100)")
    total_score = models.FloatField(null=True, blank=True, 
                                   help_text="Overall score (0-100)")
    top_dimensions = models.JSONField(default=list, blank=True,
                                     help_text="Top 3 dimensions")
    
    # PDF report
    pdf_report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.test.name} ({self.status})"


class ReportParagraphMapping(models.Model):
    """Model for storing report paragraph mappings for different dimension scores."""
    dimension = models.CharField(max_length=50, help_text="Career dimension")
    score_range_min = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         help_text="Minimum score for this range")
    score_range_max = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         help_text="Maximum score for this range")
    paragraph_text = models.TextField(help_text="Report paragraph text for this score range")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['dimension', 'score_range_min']
    
    def __str__(self):
        return f"{self.dimension}: {self.score_range_min}-{self.score_range_max}"
