"""
Management command to seed initial data.
"""
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from assessments.models import Question, Test, TestQuestion, ReportParagraphMapping


class Command(BaseCommand):
    help = 'Seed database with initial test data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Seed questions if CSV exists
        csv_path = os.path.join(settings.BASE_DIR, 'assessments', 'seed', 'question_bank_template.csv')
        if os.path.exists(csv_path):
            from django.core.management import call_command
            call_command('import_questions', csv_path)
        
        # Seed report paragraph mappings
        self.seed_report_paragraphs()
        
        # Create a sample test
        self.create_sample_test()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def seed_report_paragraphs(self):
        """Seed report paragraph mappings."""
        json_path = os.path.join(
            settings.BASE_DIR,
            'assessments',
            'seed',
            'report_paragraph_mappings.json'
        )
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                mappings = json.load(f)
                
                for mapping in mappings:
                    ReportParagraphMapping.objects.get_or_create(
                        category=mapping['category'],
                        min_score=mapping['min_score'],
                        max_score=mapping['max_score'],
                        defaults={'paragraph_text': mapping['paragraph_text']}
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Loaded {len(mappings)} report paragraph mappings'
                    )
                )
        else:
            # Create default mappings
            default_mappings = [
                {
                    'category': 'Math',
                    'min_score': 0,
                    'max_score': 50,
                    'paragraph_text': 'Your mathematical skills need strengthening. Focus on practice and fundamentals.'
                },
                {
                    'category': 'Math',
                    'min_score': 51,
                    'max_score': 75,
                    'paragraph_text': 'You have a good grasp of mathematical concepts. Keep practicing to excel.'
                },
                {
                    'category': 'Math',
                    'min_score': 76,
                    'max_score': 100,
                    'paragraph_text': 'Excellent mathematical abilities! You demonstrate strong analytical skills.'
                },
                {
                    'category': 'Verbal',
                    'min_score': 0,
                    'max_score': 50,
                    'paragraph_text': 'Work on improving your vocabulary and reading comprehension skills.'
                },
                {
                    'category': 'Verbal',
                    'min_score': 51,
                    'max_score': 75,
                    'paragraph_text': 'Your verbal skills are developing well. Continue reading and learning.'
                },
                {
                    'category': 'Verbal',
                    'min_score': 76,
                    'max_score': 100,
                    'paragraph_text': 'Outstanding verbal abilities! Your communication skills are excellent.'
                },
            ]
            
            for mapping in default_mappings:
                ReportParagraphMapping.objects.get_or_create(
                    category=mapping['category'],
                    min_score=mapping['min_score'],
                    max_score=mapping['max_score'],
                    defaults={'paragraph_text': mapping['paragraph_text']}
                )
            
            self.stdout.write(
                self.style.SUCCESS('Created default report paragraph mappings')
            )

    def create_sample_test(self):
        """Create a sample test with questions."""
        # Get some questions
        questions = Question.objects.all()[:10]
        
        if questions.exists():
            test, created = Test.objects.get_or_create(
                title='Sample Career Assessment Test',
                defaults={
                    'description': 'A sample test to assess various skills and aptitudes.',
                    'is_active': True
                }
            )
            
            if created:
                # Add questions to test
                for idx, question in enumerate(questions, 1):
                    TestQuestion.objects.get_or_create(
                        test=test,
                        question=question,
                        defaults={'order': idx}
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created sample test with {questions.count()} questions')
                )
            else:
                self.stdout.write('Sample test already exists')
        else:
            self.stdout.write(
                self.style.WARNING('No questions available to create test. Import questions first.')
            )
