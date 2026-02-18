"""
Tests for the assessments app
"""
import pytest
from django.contrib.auth.models import User
from django.test import Client
from assessments.models import Question, Test, TestQuestion, Attempt, Profile, ReportParagraphMapping
from assessments.services import compute_scores, import_questions_from_csv, get_report_paragraph
import json


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User.objects.create_user(username='testuser', password='testpass123')
    Profile.objects.create(user=user, grade=9, role='student')
    return user


@pytest.fixture
def test_questions(db):
    """Create test questions"""
    questions = []
    
    # Aptitude questions
    q1 = Question.objects.create(
        external_id='TEST001',
        grade=9,
        topic='Math',
        question_type='mcq',
        question_text='What is 2+2?',
        options=['3', '4', '5', '6'],
        correct_answer='4',
        weight=1.0,
        dimension='aptitude'
    )
    questions.append(q1)
    
    q2 = Question.objects.create(
        external_id='TEST002',
        grade=9,
        topic='Math',
        question_type='mcq',
        question_text='What is 10-5?',
        options=['3', '4', '5', '6'],
        correct_answer='5',
        weight=1.0,
        dimension='aptitude'
    )
    questions.append(q2)
    
    # Logical question
    q3 = Question.objects.create(
        external_id='TEST003',
        grade=9,
        topic='Logic',
        question_type='mcq',
        question_text='Pattern test',
        options=['A', 'B', 'C', 'D'],
        correct_answer='C',
        weight=1.0,
        dimension='logical'
    )
    questions.append(q3)
    
    # Interest rating question
    q4 = Question.objects.create(
        external_id='TEST004',
        grade=9,
        topic='Career',
        question_type='rating',
        question_text='I enjoy technical work',
        options=[],
        correct_answer='5',
        weight=1.0,
        dimension='interest'
    )
    questions.append(q4)
    
    return questions


@pytest.fixture
def test_assessment(db, test_questions):
    """Create a test assessment"""
    test = Test.objects.create(
        name='Grade 9 Test',
        grade=9,
        duration_minutes=30
    )
    
    for idx, question in enumerate(test_questions, start=1):
        TestQuestion.objects.create(
            test=test,
            question=question,
            sequence=idx
        )
    
    return test


@pytest.mark.django_db
class TestComputeScores:
    """Test the scoring engine"""
    
    def test_compute_scores_all_correct(self, test_user, test_assessment):
        """Test scoring with all correct answers"""
        attempt = Attempt.objects.create(
            test=test_assessment,
            user=test_user,
            raw_answers={
                '1': '4',  # Correct
                '2': '5',  # Correct
                '3': 'C',  # Correct
                '4': '5',  # Max rating
            }
        )
        
        result = compute_scores(attempt)
        
        assert 'dimension_scores' in result
        assert 'total_score' in result
        assert 'top_dimensions' in result
        assert result['dimension_scores']['aptitude'] == 100.0
        assert result['dimension_scores']['logical'] == 100.0
        assert result['dimension_scores']['interest'] == 100.0
        assert result['total_score'] > 0
    
    def test_compute_scores_partial_correct(self, test_user, test_assessment):
        """Test scoring with some correct answers"""
        attempt = Attempt.objects.create(
            test=test_assessment,
            user=test_user,
            raw_answers={
                '1': '4',  # Correct
                '2': '3',  # Wrong
                '3': 'A',  # Wrong
                '4': '3',  # Middle rating
            }
        )
        
        result = compute_scores(attempt)
        
        assert result['dimension_scores']['aptitude'] == 50.0  # 1 of 2 correct
        assert result['dimension_scores']['logical'] == 0.0    # 0 of 1 correct
        assert result['dimension_scores']['interest'] == 60.0  # 3/5 rating
    
    def test_compute_scores_no_answers(self, test_user, test_assessment):
        """Test scoring with no answers"""
        attempt = Attempt.objects.create(
            test=test_assessment,
            user=test_user,
            raw_answers={}
        )
        
        result = compute_scores(attempt)
        
        assert result['total_score'] == 0
        assert all(score == 0 for score in result['dimension_scores'].values())


@pytest.mark.django_db
class TestCSVImport:
    """Test CSV import functionality"""
    
    def test_import_questions_from_csv(self):
        """Test importing questions from CSV"""
        csv_content = """external_id,grade,topic,question_type,question_text,options,correct_answer,weight,dimension
CSV001,9,Math,mcq,Test question?,"[""A"",""B"",""C""]",B,1.0,aptitude
CSV002,9,Logic,mcq,Logic test?,"[""X"",""Y"",""Z""]",Y,1.5,logical"""
        
        result = import_questions_from_csv(csv_content)
        
        assert result['created'] == 2
        assert result['updated'] == 0
        assert Question.objects.filter(external_id='CSV001').exists()
        assert Question.objects.filter(external_id='CSV002').exists()
        
        q = Question.objects.get(external_id='CSV002')
        assert q.weight == 1.5
        assert q.dimension == 'logical'
    
    def test_import_questions_update_existing(self):
        """Test updating existing questions via CSV import"""
        # Create initial question
        Question.objects.create(
            external_id='UPD001',
            grade=9,
            topic='Old Topic',
            question_type='mcq',
            question_text='Old question',
            options=['A', 'B'],
            correct_answer='A',
            weight=1.0,
            dimension='aptitude'
        )
        
        csv_content = """external_id,grade,topic,question_type,question_text,options,correct_answer,weight,dimension
UPD001,9,New Topic,mcq,Updated question,"[""X"",""Y""]",X,2.0,logical"""
        
        result = import_questions_from_csv(csv_content)
        
        assert result['created'] == 0
        assert result['updated'] == 1
        
        q = Question.objects.get(external_id='UPD001')
        assert q.topic == 'New Topic'
        assert q.question_text == 'Updated question'
        assert q.weight == 2.0


@pytest.mark.django_db
class TestAttemptAPI:
    """Test attempt submission API"""
    
    def test_submit_attempt(self, test_user, test_assessment):
        """Test submitting an attempt via API"""
        client = Client()
        client.force_login(test_user)
        
        response = client.post(
            '/api/attempts/submit/',
            data=json.dumps({
                'test_id': test_assessment.id,
                'answers': {
                    '1': '4',
                    '2': '5',
                    '3': 'C',
                    '4': '5',
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'attempt_id' in data
        assert 'scores' in data
        assert 'total_score' in data
        
        # Check that attempt was saved
        attempt = Attempt.objects.get(id=data['attempt_id'])
        assert attempt.completed_at is not None
        assert attempt.total_score > 0
    
    def test_autosave_attempt(self, test_user, test_assessment):
        """Test autosaving partial answers"""
        client = Client()
        client.force_login(test_user)
        
        # Create attempt
        attempt = Attempt.objects.create(
            test=test_assessment,
            user=test_user,
            raw_answers={}
        )
        
        # Autosave partial answers
        response = client.post(
            '/api/attempts/autosave/',
            data=json.dumps({
                'attempt_id': attempt.id,
                'answers': {
                    '1': '4',
                    '2': '5',
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Check that answers were saved
        attempt.refresh_from_db()
        assert '1' in attempt.raw_answers
        assert attempt.raw_answers['1'] == '4'


@pytest.mark.django_db
class TestReportParagraphs:
    """Test report paragraph generation"""
    
    def test_get_report_paragraph(self):
        """Test retrieving report paragraphs"""
        ReportParagraphMapping.objects.create(
            dimension='aptitude',
            score_range='61-100',
            student_paragraph='You did great!',
            parent_paragraph='Your child excels.'
        )
        
        # Test high score
        student_text = get_report_paragraph('aptitude', 85, 'student')
        assert student_text == 'You did great!'
        
        parent_text = get_report_paragraph('aptitude', 85, 'parent')
        assert parent_text == 'Your child excels.'
    
    def test_get_report_paragraph_ranges(self):
        """Test different score ranges"""
        ReportParagraphMapping.objects.create(
            dimension='logical',
            score_range='0-30',
            student_paragraph='Low score text',
            parent_paragraph='Parent low text'
        )
        ReportParagraphMapping.objects.create(
            dimension='logical',
            score_range='31-60',
            student_paragraph='Medium score text',
            parent_paragraph='Parent medium text'
        )
        ReportParagraphMapping.objects.create(
            dimension='logical',
            score_range='61-100',
            student_paragraph='High score text',
            parent_paragraph='Parent high text'
        )
        
        # Test low range
        assert 'Low score text' in get_report_paragraph('logical', 25, 'student')
        
        # Test medium range
        assert 'Medium score text' in get_report_paragraph('logical', 45, 'student')
        
        # Test high range
        assert 'High score text' in get_report_paragraph('logical', 85, 'student')

