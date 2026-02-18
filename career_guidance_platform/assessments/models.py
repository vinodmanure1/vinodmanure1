from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Represents a single assessment question.
    """
    text = models.TextField(help_text="The question text")
    dimension = models.CharField(
        max_length=100,
        help_text="Career dimension this question assesses (e.g., 'Technical', 'Leadership')"
    )
    weight = models.FloatField(
        default=1.0,
        help_text="Weight/importance of this question in scoring"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.dimension}: {self.text[:50]}"

    class Meta:
        ordering = ['dimension', 'id']


class Test(models.Model):
    """
    Represents an assessment test containing multiple questions.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(
        default=30,
        help_text="Test duration in minutes"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    order = models.IntegerField(default=0, help_text="Display order in the test")

    def __str__(self):
        return f"{self.test.title} - Q{self.order}: {self.question.text[:30]}"

    class Meta:
        ordering = ['test', 'order']
        unique_together = ['test', 'question']


class Profile(models.Model):
    """
    Extended user profile for students.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    school = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class Attempt(models.Model):
    """
    Records a student's attempt at a test.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    answers = models.JSONField(
        default=dict,
        help_text="Dictionary mapping question_id to answer value"
    )
    scores = models.JSONField(
        default=dict,
        help_text="Computed scores by dimension and total"
    )
    total_score = models.FloatField(default=0.0)
    top_dimensions = models.JSONField(
        default=list,
        help_text="List of top scoring dimensions"
    )
    pdf_report_file = models.FileField(
        upload_to='reports/',
        blank=True,
        null=True,
        help_text="Generated PDF report"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.started_at}"

    class Meta:
        ordering = ['-started_at']


class ReportParagraphMapping(models.Model):
    """
    Maps dimension ranges to report text paragraphs.
    """
    dimension = models.CharField(max_length=100)
    min_score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=100.0)
    paragraph_text = models.TextField(
        help_text="Text to display in report for this score range"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dimension}: {self.min_score}-{self.max_score}"

    class Meta:
        ordering = ['dimension', 'min_score']
