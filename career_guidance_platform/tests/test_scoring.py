"""
Tests for the scoring engine.
"""
import pytest
from django.contrib.auth.models import User
from assessments.models import Question, Test, TestQuestion
from assessments.services import compute_scores


@pytest.fixture
def test_user(db):
    """Create a test user"""
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def sample_questions(db):
    """Create sample questions across different dimensions"""
    questions = []
    dimensions = ['Technical', 'Leadership', 'Creative']
    
    for i, dimension in enumerate(dimensions):
        q = Question.objects.create(
            text=f"Question about {dimension}",
            dimension=dimension,
            weight=1.0
        )
        questions.append(q)
    
    return questions


@pytest.fixture
def sample_test(db, sample_questions):
    """Create a test with sample questions"""
    test = Test.objects.create(
        title='Sample Test',
        description='Test description',
        duration_minutes=20,
        is_active=True
    )
    
    for i, question in enumerate(sample_questions):
        TestQuestion.objects.create(
            test=test,
            question=question,
            order=i + 1
        )
    
    return test


@pytest.mark.django_db
class TestComputeScores:
    """Test the compute_scores function"""
    
    def test_compute_scores_all_perfect(self, sample_test):
        """Test scoring with all 10/10 answers"""
        # Create answers dict with all questions answered 10
        answers = {}
        for tq in sample_test.test_questions.all():
            answers[str(tq.question.id)] = 10
        
        result = compute_scores(answers, sample_test)
        
        assert result['total_score'] == 100.0
        assert all(score == 100.0 for score in result['dimension_scores'].values())
        assert len(result['top_dimensions']) == 3
    
    def test_compute_scores_all_zero(self, sample_test):
        """Test scoring with all 0/10 answers"""
        answers = {}
        for tq in sample_test.test_questions.all():
            answers[str(tq.question.id)] = 0
        
        result = compute_scores(answers, sample_test)
        
        assert result['total_score'] == 0.0
        assert all(score == 0.0 for score in result['dimension_scores'].values())
    
    def test_compute_scores_mixed(self, sample_test):
        """Test scoring with mixed answers"""
        test_questions = list(sample_test.test_questions.all())
        answers = {
            str(test_questions[0].question.id): 10,  # Technical: 100%
            str(test_questions[1].question.id): 5,   # Leadership: 50%
            str(test_questions[2].question.id): 0,   # Creative: 0%
        }
        
        result = compute_scores(answers, sample_test)
        
        assert result['dimension_scores']['Technical'] == 100.0
        assert result['dimension_scores']['Leadership'] == 50.0
        assert result['dimension_scores']['Creative'] == 0.0
        assert result['total_score'] == 50.0  # Average of 100, 50, 0
        
        # Check top dimensions are sorted
        assert result['top_dimensions'][0][0] == 'Technical'
        assert result['top_dimensions'][0][1] == 100.0
    
    def test_compute_scores_empty_answers(self, sample_test):
        """Test scoring with no answers provided"""
        answers = {}
        
        result = compute_scores(answers, sample_test)
        
        # All unanswered questions should default to 0
        assert result['total_score'] == 0.0
    
    def test_compute_scores_weighted(self, db, sample_test):
        """Test scoring with weighted questions"""
        # Modify weights
        questions = list(sample_test.test_questions.all())
        questions[0].question.weight = 2.0  # Technical has double weight
        questions[0].question.save()
        
        answers = {
            str(questions[0].question.id): 10,  # Technical: weight 2.0
            str(questions[1].question.id): 0,   # Leadership: weight 1.0
            str(questions[2].question.id): 0,   # Creative: weight 1.0
        }
        
        result = compute_scores(answers, sample_test)
        
        # Technical should still be 100% (10/10 * 100)
        assert result['dimension_scores']['Technical'] == 100.0
        assert result['dimension_scores']['Leadership'] == 0.0
        assert result['dimension_scores']['Creative'] == 0.0
