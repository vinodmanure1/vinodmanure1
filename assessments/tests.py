from django.test import TestCase, Client
from django.urls import reverse
from .models import Question, StudentResponse, CareerRecommendation
from .services import CareerScoringService


class QuestionModelTest(TestCase):
    """Test the Question model."""
    
    def setUp(self):
        self.question = Question.objects.create(
            text="I enjoy solving complex problems",
            category="analytical",
            weight=2
        )
    
    def test_question_creation(self):
        """Test that a question can be created."""
        self.assertEqual(self.question.text, "I enjoy solving complex problems")
        self.assertEqual(self.question.category, "analytical")
        self.assertEqual(self.question.weight, 2)
    
    def test_question_str(self):
        """Test the string representation of a question."""
        self.assertIn("analytical", str(self.question))


class StudentResponseModelTest(TestCase):
    """Test the StudentResponse model."""
    
    def setUp(self):
        self.question = Question.objects.create(
            text="I enjoy working with technology",
            category="technical",
            weight=1
        )
        self.response = StudentResponse.objects.create(
            student_name="John Doe",
            student_email="john@example.com",
            question=self.question,
            rating=5
        )
    
    def test_response_creation(self):
        """Test that a response can be created."""
        self.assertEqual(self.response.student_name, "John Doe")
        self.assertEqual(self.response.rating, 5)
        self.assertEqual(self.response.question, self.question)
    
    def test_unique_constraint(self):
        """Test that a student can only respond once per question."""
        with self.assertRaises(Exception):
            StudentResponse.objects.create(
                student_name="John Doe",
                student_email="john@example.com",
                question=self.question,
                rating=3
            )


class CareerScoringServiceTest(TestCase):
    """Test the CareerScoringService."""
    
    def setUp(self):
        # Create test questions
        self.tech_q1 = Question.objects.create(
            text="I enjoy coding",
            category="technical",
            weight=1
        )
        self.tech_q2 = Question.objects.create(
            text="I like building software",
            category="technical",
            weight=2
        )
        self.creative_q = Question.objects.create(
            text="I enjoy design work",
            category="creative",
            weight=1
        )
        
        # Create test responses
        StudentResponse.objects.create(
            student_name="Jane Doe",
            student_email="jane@example.com",
            question=self.tech_q1,
            rating=5
        )
        StudentResponse.objects.create(
            student_name="Jane Doe",
            student_email="jane@example.com",
            question=self.tech_q2,
            rating=4
        )
        StudentResponse.objects.create(
            student_name="Jane Doe",
            student_email="jane@example.com",
            question=self.creative_q,
            rating=2
        )
    
    def test_calculate_scores(self):
        """Test score calculation."""
        scores = CareerScoringService.calculate_scores("jane@example.com")
        self.assertIn("technical", scores)
        self.assertIn("creative", scores)
        self.assertGreater(scores["technical"], scores["creative"])
    
    def test_get_career_recommendations(self):
        """Test career recommendation generation."""
        scores = {"technical": 90, "creative": 40, "analytical": 60}
        primary, alternatives = CareerScoringService.get_career_recommendations(scores)
        self.assertIn("Software", primary)
        self.assertIsInstance(alternatives, list)
    
    def test_create_recommendation(self):
        """Test creating a career recommendation."""
        recommendation = CareerScoringService.create_or_update_recommendation(
            "jane@example.com",
            "Jane Doe"
        )
        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation.student_email, "jane@example.com")
        self.assertGreater(recommendation.technical_score, 0)


class ViewsTest(TestCase):
    """Test views."""
    
    def setUp(self):
        self.client = Client()
        # Create test questions
        for i in range(3):
            Question.objects.create(
                text=f"Test question {i}",
                category="technical",
                weight=1
            )
    
    def test_home_view(self):
        """Test home page loads."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Career Guidance Platform")
    
    def test_assessment_view_get(self):
        """Test assessment page loads with questions."""
        response = self.client.get(reverse('assessment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Career Assessment")
        self.assertContains(response, "Test question")
    
    def test_assessment_view_post(self):
        """Test submitting assessment."""
        questions = Question.objects.all()
        post_data = {
            'student_name': 'Test Student',
            'student_email': 'test@example.com',
        }
        for question in questions:
            post_data[f'question_{question.id}'] = '4'
        
        response = self.client.post(reverse('assessment'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check that responses were created
        self.assertEqual(
            StudentResponse.objects.filter(student_email='test@example.com').count(),
            questions.count()
        )
    
    def test_results_view(self):
        """Test results view with recommendation."""
        # Create a recommendation
        recommendation = CareerRecommendation.objects.create(
            student_name="Test Student",
            student_email="test@example.com",
            technical_score=85.0,
            creative_score=60.0,
            analytical_score=70.0,
            social_score=55.0,
            practical_score=65.0,
            recommended_career="Software Developer",
            alternative_careers=["Data Scientist", "Systems Engineer"]
        )
        
        response = self.client.get(reverse('results', kwargs={'email': 'test@example.com'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Software Developer")
        self.assertContains(response, "Test Student")
