from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Career, Assessment, Question, Answer, Result
from .services import AssessmentScoringService


class CareerModelTest(TestCase):
    def setUp(self):
        self.career = Career.objects.create(
            name='Software Engineer',
            description='Develops software applications',
            industry='Technology',
            average_salary=100000.00,
            growth_rate=15.5
        )

    def test_career_creation(self):
        self.assertEqual(self.career.name, 'Software Engineer')
        self.assertEqual(self.career.industry, 'Technology')
        self.assertEqual(str(self.career), 'Software Engineer')


class AssessmentModelTest(TestCase):
    def setUp(self):
        self.assessment = Assessment.objects.create(
            title='Career Interest Assessment',
            description='Find your ideal career',
            duration_minutes=20,
            is_active=True
        )

    def test_assessment_creation(self):
        self.assertEqual(self.assessment.title, 'Career Interest Assessment')
        self.assertTrue(self.assessment.is_active)
        self.assertEqual(str(self.assessment), 'Career Interest Assessment')


class QuestionAnswerModelTest(TestCase):
    def setUp(self):
        self.career = Career.objects.create(
            name='Data Scientist',
            description='Analyzes data',
            industry='Technology'
        )
        self.assessment = Assessment.objects.create(
            title='Test Assessment',
            description='Test',
            duration_minutes=10
        )
        self.question = Question.objects.create(
            assessment=self.assessment,
            text='What interests you?',
            question_type='MULTIPLE_CHOICE',
            order=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Working with data',
            career=self.career,
            score=10,
            order=1
        )

    def test_question_creation(self):
        self.assertEqual(self.question.assessment, self.assessment)
        self.assertEqual(self.question.question_type, 'MULTIPLE_CHOICE')

    def test_answer_creation(self):
        self.assertEqual(self.answer.question, self.question)
        self.assertEqual(self.answer.career, self.career)
        self.assertEqual(self.answer.score, 10)


class AssessmentScoringServiceTest(TestCase):
    def setUp(self):
        self.career1 = Career.objects.create(
            name='Engineer',
            description='Engineering career',
            industry='Technology'
        )
        self.career2 = Career.objects.create(
            name='Designer',
            description='Design career',
            industry='Creative'
        )
        self.assessment = Assessment.objects.create(
            title='Test Assessment',
            description='Test',
            duration_minutes=10
        )
        self.question1 = Question.objects.create(
            assessment=self.assessment,
            text='Question 1',
            order=1
        )
        self.answer1 = Answer.objects.create(
            question=self.question1,
            text='Answer 1',
            career=self.career1,
            score=10,
            order=1
        )
        self.answer2 = Answer.objects.create(
            question=self.question1,
            text='Answer 2',
            career=self.career2,
            score=5,
            order=2
        )

    def test_calculate_scores(self):
        responses = {str(self.question1.id): self.answer1.id}
        scores = AssessmentScoringService.calculate_scores(self.assessment.id, responses)
        self.assertEqual(scores[self.career1.id], 10)

    def test_get_recommended_career(self):
        scores = {self.career1.id: 10, self.career2.id: 5}
        recommended = AssessmentScoringService.get_recommended_career(scores)
        self.assertEqual(recommended, self.career1)

    def test_create_result(self):
        responses = {str(self.question1.id): self.answer1.id}
        result = AssessmentScoringService.create_result(
            assessment_id=self.assessment.id,
            responses=responses,
            student_name='Test Student',
            student_email='test@example.com'
        )
        self.assertEqual(result.assessment, self.assessment)
        self.assertEqual(result.student_name, 'Test Student')
        self.assertEqual(result.recommended_career, self.career1)


class StudentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.career = Career.objects.create(
            name='Test Career',
            description='Test',
            industry='Test'
        )
        self.assessment = Assessment.objects.create(
            title='Test Assessment',
            description='Test',
            duration_minutes=10,
            is_active=True
        )
        self.question = Question.objects.create(
            assessment=self.assessment,
            text='Test Question',
            order=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            text='Test Answer',
            career=self.career,
            score=10,
            order=1
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Assessment')

    def test_take_assessment_view_get(self):
        response = self.client.get(reverse('take_assessment', args=[self.assessment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Assessment')
        self.assertContains(response, 'Test Question')

    def test_take_assessment_view_post(self):
        response = self.client.post(
            reverse('take_assessment', args=[self.assessment.id]),
            {
                f'question_{self.question.id}': self.answer.id,
                'student_name': 'Test Student',
                'student_email': 'test@example.com'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect to result
        self.assertEqual(Result.objects.count(), 1)


class APIViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.assessment = Assessment.objects.create(
            title='API Test Assessment',
            description='Test',
            duration_minutes=10,
            is_active=True
        )

    def test_list_assessments_api(self):
        response = self.client.get(reverse('api_list_assessments'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 1)

    def test_get_assessment_api(self):
        response = self.client.get(reverse('api_get_assessment', args=[self.assessment.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['title'], 'API Test Assessment')
