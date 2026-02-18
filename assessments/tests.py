"""
Tests for the assessments app.
"""
import pytest
from django.contrib.auth.models import User
from assessments.models import Question, Test, TestQuestion, Attempt, Profile
from assessments.services import compute_scores, get_feedback_for_score


@pytest.fixture
def sample_questions(db):
    """Create sample questions for testing."""
    q1 = Question.objects.create(
        question_text="What is 2+2?",
        option_a="3",
        option_b="4",
        option_c="5",
        option_d="6",
        correct_answer="B",
        category="Math",
        difficulty="Easy"
    )
    q2 = Question.objects.create(
        question_text="What is 3+3?",
        option_a="5",
        option_b="6",
        option_c="7",
        option_d="8",
        correct_answer="B",
        category="Math",
        difficulty="Easy"
    )
    q3 = Question.objects.create(
        question_text="Choose synonym for 'big'",
        option_a="Small",
        option_b="Large",
        option_c="Tiny",
        option_d="Little",
        correct_answer="B",
        category="Verbal",
        difficulty="Easy"
    )
    return [q1, q2, q3]


@pytest.fixture
def sample_test(db, sample_questions):
    """Create a sample test with questions."""
    test = Test.objects.create(
        title="Sample Test",
        description="A test for testing",
        is_active=True
    )
    
    for idx, question in enumerate(sample_questions, 1):
        TestQuestion.objects.create(
            test=test,
            question=question,
            order=idx
        )
    
    return test


@pytest.mark.django_db
class TestComputeScores:
    """Tests for the compute_scores function."""
    
    def test_compute_scores_all_correct(self, sample_test, sample_questions):
        """Test scoring when all answers are correct."""
        answers = {
            str(sample_questions[0].id): "B",
            str(sample_questions[1].id): "B",
            str(sample_questions[2].id): "B",
        }
        
        scores = compute_scores(sample_test.id, answers)
        
        assert scores['total_score']['correct'] == 3
        assert scores['total_score']['total'] == 3
        assert scores['total_score']['percentage'] == 100.0
        
        assert scores['category_scores']['Math']['correct'] == 2
        assert scores['category_scores']['Math']['total'] == 2
        assert scores['category_scores']['Math']['percentage'] == 100.0
        
        assert scores['category_scores']['Verbal']['correct'] == 1
        assert scores['category_scores']['Verbal']['total'] == 1
        assert scores['category_scores']['Verbal']['percentage'] == 100.0
    
    def test_compute_scores_all_wrong(self, sample_test, sample_questions):
        """Test scoring when all answers are wrong."""
        answers = {
            str(sample_questions[0].id): "A",
            str(sample_questions[1].id): "A",
            str(sample_questions[2].id): "A",
        }
        
        scores = compute_scores(sample_test.id, answers)
        
        assert scores['total_score']['correct'] == 0
        assert scores['total_score']['total'] == 3
        assert scores['total_score']['percentage'] == 0.0
        
        assert scores['category_scores']['Math']['correct'] == 0
        assert scores['category_scores']['Math']['percentage'] == 0.0
        
        assert scores['category_scores']['Verbal']['correct'] == 0
        assert scores['category_scores']['Verbal']['percentage'] == 0.0
    
    def test_compute_scores_mixed(self, sample_test, sample_questions):
        """Test scoring with mixed correct/incorrect answers."""
        answers = {
            str(sample_questions[0].id): "B",  # Correct
            str(sample_questions[1].id): "A",  # Wrong
            str(sample_questions[2].id): "B",  # Correct
        }
        
        scores = compute_scores(sample_test.id, answers)
        
        assert scores['total_score']['correct'] == 2
        assert scores['total_score']['total'] == 3
        assert round(scores['total_score']['percentage'], 2) == 66.67
        
        assert scores['category_scores']['Math']['correct'] == 1
        assert scores['category_scores']['Math']['total'] == 2
        assert scores['category_scores']['Math']['percentage'] == 50.0
        
        assert scores['category_scores']['Verbal']['correct'] == 1
        assert scores['category_scores']['Verbal']['percentage'] == 100.0
    
    def test_compute_scores_missing_answers(self, sample_test, sample_questions):
        """Test scoring when some answers are missing."""
        answers = {
            str(sample_questions[0].id): "B",  # Only first question answered
        }
        
        scores = compute_scores(sample_test.id, answers)
        
        # Missing answers should be counted as wrong
        assert scores['total_score']['correct'] == 1
        assert scores['total_score']['total'] == 3


@pytest.mark.django_db
class TestAttemptCreation:
    """Integration tests for creating attempts."""
    
    def test_create_attempt(self, sample_test):
        """Test creating an attempt with scores."""
        answers = {"1": "A", "2": "B"}
        scores = {"total_score": {"percentage": 50.0}}
        
        attempt = Attempt.objects.create(
            test=sample_test,
            student_name="Test Student",
            student_email="test@example.com",
            answers=answers,
            scores=scores
        )
        
        assert attempt.id is not None
        assert attempt.student_name == "Test Student"
        assert attempt.answers == answers
        assert attempt.scores == scores
        assert attempt.test == sample_test
