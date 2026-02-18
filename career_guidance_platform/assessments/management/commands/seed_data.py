"""
Management command to seed initial data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assessments.models import Test, Question, TestQuestion


class Command(BaseCommand):
    help = 'Seed initial data (admin user and sample test)'

    def handle(self, *args, **options):
        # Create admin user if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created admin user (username: admin, password: admin123)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )
        
        # Create test student user
        if not User.objects.filter(username='student').exists():
            User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created student user (username: student, password: student123)')
            )
        
        # Create a sample test if there are questions
        questions = Question.objects.all()
        if questions.exists():
            if not Test.objects.filter(title='Career Interest Assessment').exists():
                test = Test.objects.create(
                    title='Career Interest Assessment',
                    description='Discover your career interests and strengths',
                    duration_minutes=20,
                    is_active=True
                )
                
                # Add all questions to the test
                for idx, question in enumerate(questions, start=1):
                    TestQuestion.objects.create(
                        test=test,
                        question=question,
                        order=idx
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created sample test with {questions.count()} questions'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Sample test already exists')
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No questions found. Run import_questions first.'
                )
            )
