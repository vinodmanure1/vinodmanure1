from django.test import TestCase
from django.contrib.auth.models import User
from assessments.models import Question, Test, TestQuestion, Attempt
from assessments.services import compute_scores


class ServicesTestCase(TestCase):
    """Test cases for assessment services."""
    
    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create questions
        self.q1 = Question.objects.create(
            text='Test question 1',
            category='technical',
            option_a='A', option_b='B', option_c='C', option_d='D',
            correct_answer='A'
        )
        self.q2 = Question.objects.create(
            text='Test question 2',
            category='technical',
            option_a='A', option_b='B', option_c='C', option_d='D',
            correct_answer='B'
        )
        self.q3 = Question.objects.create(
            text='Test question 3',
            category='creative',
            option_a='A', option_b='B', option_c='C', option_d='D',
            correct_answer='C'
        )
        
        # Create test
        self.test = Test.objects.create(
            name='Test Assessment',
            description='Test description',
            duration_minutes=30
        )
        
        # Add questions to test
        TestQuestion.objects.create(test=self.test, question=self.q1, order=1)
        TestQuestion.objects.create(test=self.test, question=self.q2, order=2)
        TestQuestion.objects.create(test=self.test, question=self.q3, order=3)
    
    def test_compute_scores_all_correct(self):
        """Test score computation with all correct answers."""
        attempt = Attempt.objects.create(
            user=self.user,
            test=self.test,
            status='in_progress',
            answers={
                str(self.q1.id): 'A',
                str(self.q2.id): 'B',
                str(self.q3.id): 'C'
            }
        )
        
        scores = compute_scores(attempt)
        
        # Check overall score
        self.assertEqual(attempt.total_score, 3)
        self.assertEqual(attempt.percentage, 100.0)
        self.assertEqual(attempt.status, 'completed')
        
        # Check category scores
        self.assertIn('technical', scores)
        self.assertIn('creative', scores)
        self.assertEqual(scores['technical']['correct'], 2)
        self.assertEqual(scores['technical']['total'], 2)
        self.assertEqual(scores['technical']['percentage'], 100.0)
        self.assertEqual(scores['creative']['correct'], 1)
        self.assertEqual(scores['creative']['total'], 1)
        self.assertEqual(scores['creative']['percentage'], 100.0)
    
    def test_compute_scores_partial_correct(self):
        """Test score computation with some correct answers."""
        attempt = Attempt.objects.create(
            user=self.user,
            test=self.test,
            status='in_progress',
            answers={
                str(self.q1.id): 'A',  # Correct
                str(self.q2.id): 'A',  # Incorrect (should be B)
                str(self.q3.id): 'C'   # Correct
            }
        )
        
        scores = compute_scores(attempt)
        
        # Check overall score
        self.assertEqual(attempt.total_score, 2)
        self.assertAlmostEqual(attempt.percentage, 66.67, places=1)
        
        # Check category scores
        self.assertEqual(scores['technical']['correct'], 1)
        self.assertEqual(scores['technical']['total'], 2)
        self.assertEqual(scores['technical']['percentage'], 50.0)
        self.assertEqual(scores['creative']['correct'], 1)
        self.assertEqual(scores['creative']['total'], 1)
        self.assertEqual(scores['creative']['percentage'], 100.0)
    
    def test_compute_scores_no_answers(self):
        """Test score computation with no answers."""
        attempt = Attempt.objects.create(
            user=self.user,
            test=self.test,
            status='in_progress',
            answers={}
        )
        
        scores = compute_scores(attempt)
        
        # Check overall score
        self.assertEqual(attempt.total_score, 0)
        self.assertEqual(attempt.percentage, 0.0)
    
    def test_compute_scores_missing_answers(self):
        """Test score computation with missing answers."""
        attempt = Attempt.objects.create(
            user=self.user,
            test=self.test,
            status='in_progress',
            answers={
                str(self.q1.id): 'A',  # Correct
                # q2 missing
                str(self.q3.id): 'C'   # Correct
            }
        )
        
        scores = compute_scores(attempt)
        
        # Check overall score (2 correct out of 3)
        self.assertEqual(attempt.total_score, 2)
        self.assertAlmostEqual(attempt.percentage, 66.67, places=1)
