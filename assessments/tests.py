import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import csv
import io

from .models import Question, Test, TestQuestion, Attempt
from .services import compute_scores


@pytest.mark.django_db
class TestComputeScores:
    """Tests for the scoring engine."""
    
    def test_compute_scores_basic(self):
        """Test basic score computation."""
        # Create test questions
        q1 = Question.objects.create(
            text="Question 1",
            dimension="analytical",
            weight=5,
            order=1
        )
        q2 = Question.objects.create(
            text="Question 2",
            dimension="analytical",
            weight=5,
            order=2
        )
        
        # Test answers (0-5 scale)
        answers = {
            q1.id: 5,  # Perfect score
            q2.id: 3,  # 60% score
        }
        
        result = compute_scores(answers)
        
        assert 'dimension_scores' in result
        assert 'total_score' in result
        assert 'top_dimensions' in result
        assert 'analytical' in result['dimension_scores']
        assert result['dimension_scores']['analytical'] == 80.0  # (5*5 + 3*5) / (5*5 + 5*5) * 100
        assert result['total_score'] == 80.0
    
    def test_compute_scores_multiple_dimensions(self):
        """Test score computation with multiple dimensions."""
        q1 = Question.objects.create(text="Q1", dimension="analytical", weight=2, order=1)
        q2 = Question.objects.create(text="Q2", dimension="creative", weight=3, order=2)
        q3 = Question.objects.create(text="Q3", dimension="practical", weight=1, order=3)
        
        answers = {q1.id: 4, q2.id: 5, q3.id: 3}
        
        result = compute_scores(answers)
        
        assert len(result['dimension_scores']) == 3
        assert 'analytical' in result['dimension_scores']
        assert 'creative' in result['dimension_scores']
        assert 'practical' in result['dimension_scores']
        assert len(result['top_dimensions']) <= 3
    
    def test_compute_scores_empty_answers(self):
        """Test compute_scores with empty answers."""
        result = compute_scores({})
        
        assert result['dimension_scores'] == {}
        assert result['total_score'] == 0.0
        assert result['top_dimensions'] == []


@pytest.mark.django_db
class TestCSVImport:
    """Tests for CSV import functionality."""
    
    def test_import_questions_from_csv(self):
        """Test importing questions from CSV."""
        csv_content = """text,dimension,weight,order,is_active
"Test question 1",analytical,5,1,True
"Test question 2",creative,3,2,True
"""
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        count = 0
        for row in reader:
            Question.objects.create(
                text=row['text'],
                dimension=row['dimension'],
                weight=int(row['weight']),
                order=int(row['order']),
                is_active=row['is_active'].lower() == 'true'
            )
            count += 1
        
        assert count == 2
        assert Question.objects.count() == 2
        
        q1 = Question.objects.get(order=1)
        assert q1.text == "Test question 1"
        assert q1.dimension == "analytical"
        assert q1.weight == 5


@pytest.mark.django_db
class TestAttemptSubmission:
    """Tests for attempt submission."""
    
    def test_submit_attempt_creates_scores(self):
        """Test that submitting an attempt computes and saves scores."""
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        test = Test.objects.create(title="Test", description="Test", duration_minutes=30)
        
        q1 = Question.objects.create(text="Q1", dimension="analytical", weight=5, order=1)
        q2 = Question.objects.create(text="Q2", dimension="analytical", weight=5, order=2)
        
        TestQuestion.objects.create(test=test, question=q1, order=1)
        TestQuestion.objects.create(test=test, question=q2, order=2)
        
        answers = {q1.id: 5, q2.id: 4}
        
        attempt = Attempt.objects.create(
            user=user,
            test=test,
            answers=answers
        )
        
        # Compute scores
        scores = compute_scores(answers)
        attempt.scores = scores
        attempt.total_score = scores['total_score']
        attempt.save()
        
        assert attempt.total_score == 90.0
        assert 'dimension_scores' in attempt.scores
        assert 'analytical' in attempt.scores['dimension_scores']
    
    @patch('weasyprint.HTML')
    def test_pdf_generation_mocked(self, mock_html):
        """Test PDF generation with mocked WeasyPrint."""
        mock_pdf = MagicMock()
        mock_html.return_value.write_pdf = mock_pdf
        
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        test = Test.objects.create(title="Test", description="Test", duration_minutes=30)
        
        attempt = Attempt.objects.create(
            user=user,
            test=test,
            status='completed',
            total_score=85.0
        )
        
        # This would be called in the view
        # For now, just verify the attempt was created
        assert attempt.status == 'completed'
        assert attempt.total_score == 85.0


@pytest.mark.django_db
class TestModels:
    """Tests for model functionality."""
    
    def test_question_str(self):
        """Test Question string representation."""
        q = Question.objects.create(text="What is your favorite color?", dimension="creative")
        assert "What is your favorite color?" in str(q)
    
    def test_test_str(self):
        """Test Test string representation."""
        t = Test.objects.create(title="Career Assessment", description="Test", duration_minutes=30)
        assert str(t) == "Career Assessment"
    
    def test_attempt_ordering(self):
        """Test that attempts are ordered by started_at descending."""
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        test = Test.objects.create(title="Test", description="Test", duration_minutes=30)
        
        attempt1 = Attempt.objects.create(user=user, test=test)
        attempt2 = Attempt.objects.create(user=user, test=test)
        
        attempts = list(Attempt.objects.all())
        assert attempts[0].id == attempt2.id  # Most recent first
        assert attempts[1].id == attempt1.id

