"""
Management command to seed the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assessments.models import Test, TestQuestion, Question, ReportParagraphMapping


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create admin user if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user (admin/admin123)'))
        
        # Create sample test if doesn't exist
        if not Test.objects.filter(name='Career Aptitude Test').exists():
            test = Test.objects.create(
                name='Career Aptitude Test',
                description='A comprehensive test to assess your career aptitudes across multiple dimensions.',
                duration_minutes=20,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created test: {test.name}'))
            
            # Link questions to test
            questions = Question.objects.all()
            if questions:
                for idx, question in enumerate(questions, start=1):
                    TestQuestion.objects.get_or_create(
                        test=test,
                        question=question,
                        defaults={'order': idx}
                    )
                self.stdout.write(self.style.SUCCESS(f'Linked {questions.count()} questions to test'))
        
        # Create sample report paragraph mappings
        dimensions = ['technical', 'creative', 'analytical', 'leadership', 'communication']
        
        for dimension in dimensions:
            # Low score (0-40)
            ReportParagraphMapping.objects.get_or_create(
                dimension=dimension,
                score_range_min=0,
                score_range_max=40,
                defaults={
                    'paragraph_text': f'Your {dimension} skills show room for growth. Consider focusing on developing these abilities through targeted practice and learning.'
                }
            )
            
            # Medium score (41-70)
            ReportParagraphMapping.objects.get_or_create(
                dimension=dimension,
                score_range_min=41,
                score_range_max=70,
                defaults={
                    'paragraph_text': f'You demonstrate good {dimension} capabilities. With continued development, you can reach advanced proficiency in this area.'
                }
            )
            
            # High score (71-100)
            ReportParagraphMapping.objects.get_or_create(
                dimension=dimension,
                score_range_min=71,
                score_range_max=100,
                defaults={
                    'paragraph_text': f'Excellent! You show strong {dimension} abilities. This is a key strength that you should leverage in your career path.'
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created report paragraph mappings'))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
