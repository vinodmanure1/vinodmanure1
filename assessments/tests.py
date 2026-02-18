"""
Tests for the assessments app.
"""
import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from assessments.models import Question, Test, TestQuestion, Attempt
from assessments.services import compute_scores
import io
import csv
from unittest.mock import patch, MagicMock


@pytest.fixture
def db_setup(db):
    """Set up database for tests."""
    pass


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(username='admin', password='admin123')


@pytest.fixture
def sample_questions(db):
    """Create sample questions."""
    questions = []
    dimensions = ['technical', 'creative', 'analytical']
    
    for i, dim in enumerate(dimensions):
        for j in range(2):
            q = Question.objects.create(
                text=f"Question {i*2+j+1} for {dim}",
                dimension=dim,
                weight=1.0
            )
            questions.append(q)
    
    return questions


@pytest.fixture
def sample_test(db, sample_questions):
    """Create a sample test with questions."""
    test = Test.objects.create(
        name='Sample Test',
        description='A test description',
        duration_minutes=30,
        is_active=True
    )
    
    for idx, question in enumerate(sample_questions, start=1):
        TestQuestion.objects.create(
            test=test,
            question=question,
            order=idx
        )
    
    return test


@pytest.mark.django_db
class TestComputeScores:
    """Tests for the compute_scores function."""
    
    def test_compute_scores_empty_answers(self):
        """Test compute_scores with empty answers."""
        result = compute_scores({})
        
        assert result['dimension_scores'] == {}
        assert result['total_score'] == 0.0
        assert result['top_dimensions'] == []
    
    def test_compute_scores_with_answers(self, sample_questions):
        """Test compute_scores with valid answers."""
        # Create answers: all 5s (perfect scores)
        answers = {q.id: 5 for q in sample_questions}
        
        result = compute_scores(answers)
        
        # Check that we have dimension scores
        assert 'technical' in result['dimension_scores']
        assert 'creative' in result['dimension_scores']
        assert 'analytical' in result['dimension_scores']
        
        # All perfect answers should give 100 for each dimension
        for score in result['dimension_scores'].values():
            assert score == 100.0
        
        # Total score should be 100
        assert result['total_score'] == 100.0
        
        # Top dimensions should have 3 items
        assert len(result['top_dimensions']) == 3
    
    def test_compute_scores_partial_answers(self, sample_questions):
        """Test compute_scores with partial answers (score of 3 = neutral)."""
        # Create answers: all 3s (neutral/middle scores)
        answers = {q.id: 3 for q in sample_questions}
        
        result = compute_scores(answers)
        
        # Score of 3 out of 5 = (3-1)/(5-1) = 2/4 = 0.5 = 50%
        for score in result['dimension_scores'].values():
            assert score == 50.0
        
        assert result['total_score'] == 50.0
    
    def test_compute_scores_deterministic(self, sample_questions):
        """Test that compute_scores produces deterministic results."""
        answers = {q.id: 4 for q in sample_questions}
        
        result1 = compute_scores(answers)
        result2 = compute_scores(answers)
        
        assert result1 == result2


@pytest.mark.django_db
class TestCSVImport:
    """Tests for CSV import functionality."""
    
    def test_import_questions_command(self, tmp_path):
        """Test the import_questions management command."""
        # Create a temporary CSV file
        csv_file = tmp_path / "questions.csv"
        csv_file.write_text(
            "text,dimension,weight\n"
            "Test question 1,technical,1.0\n"
            "Test question 2,creative,1.5\n"
        )
        
        # Run the command
        out = io.StringIO()
        call_command('import_questions', str(csv_file), stdout=out)
        
        # Check that questions were created
        assert Question.objects.count() == 2
        assert Question.objects.filter(dimension='technical').exists()
        assert Question.objects.filter(dimension='creative').exists()
    
    def test_import_questions_invalid_dimension(self, tmp_path):
        """Test import with invalid dimension."""
        csv_file = tmp_path / "questions.csv"
        csv_file.write_text(
            "text,dimension,weight\n"
            "Test question,invalid_dimension,1.0\n"
        )
        
        out = io.StringIO()
        call_command('import_questions', str(csv_file), stdout=out)
        
        # Question should not be created
        assert Question.objects.count() == 0


@pytest.mark.django_db
class TestAttemptSubmission:
    """Tests for attempt submission."""
    
    def test_submit_attempt_api(self, user, sample_test):
        """Test submitting an attempt via API."""
        client = Client()
        client.force_login(user)
        
        # Get questions
        questions = Question.objects.all()
        answers = {str(q.id): 4 for q in questions}
        
        response = client.post(
            '/assessments/api/submit-attempt/',
            data={
                'test_id': sample_test.id,
                'answers': answers
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert 'attempt_id' in data
        assert 'dimension_scores' in data
        assert 'total_score' in data
        assert 'top_dimensions' in data
        
        # Check that attempt was created
        attempt = Attempt.objects.get(id=data['attempt_id'])
        assert attempt.user == user
        assert attempt.test == sample_test
        assert attempt.status == 'completed'
        assert attempt.total_score is not None
    
    @patch('assessments.views.HTML')
    def test_download_pdf_report(self, mock_html, user, sample_test):
        """Test PDF generation (mocked)."""
        client = Client()
        client.force_login(user)
        
        # Create a completed attempt
        attempt = Attempt.objects.create(
            user=user,
            test=sample_test,
            status='completed',
            dimension_scores={'technical': 80, 'creative': 70},
            total_score=75.0,
            top_dimensions=['technical', 'creative']
        )
        
        # Mock WeasyPrint HTML class
        mock_instance = MagicMock()
        mock_instance.write_pdf.return_value = b'fake pdf content'
        mock_html.return_value = mock_instance
        
        response = client.get(f'/assessments/report/{attempt.id}/pdf/')
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
    
    def test_autosave_attempt(self, user, sample_test):
        """Test autosaving an attempt."""
        client = Client()
        client.force_login(user)
        
        # Create an in-progress attempt
        attempt = Attempt.objects.create(
            user=user,
            test=sample_test,
            status='in_progress'
        )
        
        questions = Question.objects.all()
        answers = {str(q.id): 3 for q in questions}
        
        response = client.post(
            f'/assessments/api/autosave-attempt/{attempt.id}/',
            data={'answers': answers},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Refresh attempt from database
        attempt.refresh_from_db()
        assert len(attempt.answers) == len(questions)


@pytest.mark.django_db
class TestStudentViews:
    """Tests for student-facing views."""
    
    def test_dashboard_view(self, user):
        """Test student dashboard view."""
        client = Client()
        client.force_login(user)
        
        response = client.get('/assessments/dashboard/')
        
        assert response.status_code == 200
        assert b'Available Tests' in response.content
    
    def test_take_test_view(self, user, sample_test):
        """Test take test view."""
        client = Client()
        client.force_login(user)
        
        response = client.get(f'/assessments/take-test/{sample_test.id}/')
        
        assert response.status_code == 200
        assert sample_test.name.encode() in response.content
        
        # Check that an attempt was created
        assert Attempt.objects.filter(user=user, test=sample_test, status='in_progress').exists()

