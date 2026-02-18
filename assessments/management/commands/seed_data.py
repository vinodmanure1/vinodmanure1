"""
Management command to seed database with sample data.

Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assessments.models import Question, Test, TestQuestion, ReportParagraphMapping
import os


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin123)'))
        
        # Create test user
        if not User.objects.filter(username='student').exists():
            User.objects.create_user('student', 'student@example.com', 'student123')
            self.stdout.write(self.style.SUCCESS('Created student user (username: student, password: student123)'))
        
        # Import questions from CSV
        from django.core.management import call_command
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                'seed', 'question_bank_template.csv')
        
        if os.path.exists(csv_path):
            if not Question.objects.exists():
                call_command('import_questions', csv_path)
                self.stdout.write(self.style.SUCCESS('Imported questions from CSV'))
        
        # Create a sample test
        if not Test.objects.filter(title='Career Aptitude Assessment').exists():
            test = Test.objects.create(
                title='Career Aptitude Assessment',
                description='A comprehensive assessment to evaluate your strengths across multiple dimensions.',
                duration_minutes=30
            )
            
            # Add all questions to the test
            questions = Question.objects.all()
            for i, question in enumerate(questions):
                TestQuestion.objects.create(
                    test=test,
                    question=question,
                    order=i
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created test with {questions.count()} questions'))
        
        # Create report paragraph mappings
        if not ReportParagraphMapping.objects.exists():
            dimensions = ['analytical', 'creative', 'practical', 'social', 'leadership', 'technical']
            
            for dimension in dimensions:
                # High score (80-100)
                ReportParagraphMapping.objects.create(
                    dimension=dimension,
                    score_min=80,
                    score_max=100,
                    student_paragraph=f'Excellent! You demonstrate exceptional {dimension} abilities. '
                                     f'This is a strong area for you and can be a foundation for many career paths.',
                    parent_paragraph=f'Your child shows excellent {dimension} skills, scoring in the top tier. '
                                   f'This strength should be nurtured and can guide career exploration.'
                )
                
                # Medium score (50-79)
                ReportParagraphMapping.objects.create(
                    dimension=dimension,
                    score_min=50,
                    score_max=79,
                    student_paragraph=f'Good work! You show solid {dimension} capabilities. '
                                     f'With continued practice, you can further develop this skill.',
                    parent_paragraph=f'Your child demonstrates good {dimension} abilities. '
                                   f'Encouraging development in this area can open up various opportunities.'
                )
                
                # Low score (0-49)
                ReportParagraphMapping.objects.create(
                    dimension=dimension,
                    score_min=0,
                    score_max=49,
                    student_paragraph=f'This is an area for growth. Don\'t worry - {dimension} skills can be developed '
                                     f'through practice and learning. Consider exploring activities that build these abilities.',
                    parent_paragraph=f'Your child has potential to grow in {dimension}. '
                                   f'Support and encouragement in this area can help develop these important skills.'
                )
            
            self.stdout.write(self.style.SUCCESS('Created report paragraph mappings'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
