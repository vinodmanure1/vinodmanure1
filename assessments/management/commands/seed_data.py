import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assessments.models import Question, Test, TestQuestion, Profile, ReportParagraphMapping


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create demo user
        user, created = User.objects.get_or_create(
            username='demo_student',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'Student'
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            Profile.objects.create(
                user=user,
                full_name='Demo Student',
                email='demo@example.com'
            )
            self.stdout.write(self.style.SUCCESS('Created demo user'))
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Import questions from CSV
        csv_path = 'seed/question_bank_template.csv'
        if os.path.exists(csv_path):
            from django.core.management import call_command
            call_command('import_questions', csv_path)
        else:
            # Create sample questions if CSV doesn't exist
            self.create_sample_questions()
        
        # Create a test
        test, created = Test.objects.get_or_create(
            name='Career Assessment Test',
            defaults={
                'description': 'Comprehensive career guidance assessment',
                'duration_minutes': 30,
                'is_active': True
            }
        )
        
        if created:
            # Add questions to test
            questions = Question.objects.all()[:20]
            for idx, question in enumerate(questions, start=1):
                TestQuestion.objects.get_or_create(
                    test=test,
                    question=question,
                    defaults={'order': idx}
                )
            self.stdout.write(self.style.SUCCESS(f'Created test: {test.name}'))
        
        # Import report paragraph mappings
        json_path = 'seed/report_paragraph_mappings.json'
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                mappings = json.load(f)
                for mapping in mappings:
                    ReportParagraphMapping.objects.get_or_create(
                        category=mapping['category'],
                        min_score=mapping['min_score'],
                        max_score=mapping['max_score'],
                        defaults={
                            'title': mapping['title'],
                            'content': mapping['content'],
                            'recommendations': mapping['recommendations']
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Imported report paragraph mappings'))
        else:
            # Create default mappings
            self.create_default_mappings()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
    
    def create_sample_questions(self):
        """Create sample questions if CSV doesn't exist."""
        categories = ['technical', 'creative', 'analytical', 'interpersonal', 'leadership']
        
        for category in categories:
            for i in range(5):
                Question.objects.get_or_create(
                    text=f'Sample {category} question {i+1}?',
                    category=category,
                    defaults={
                        'option_a': 'Option A',
                        'option_b': 'Option B',
                        'option_c': 'Option C',
                        'option_d': 'Option D',
                        'correct_answer': 'A'
                    }
                )
        self.stdout.write(self.style.SUCCESS('Created sample questions'))
    
    def create_default_mappings(self):
        """Create default report paragraph mappings."""
        categories = ['technical', 'creative', 'analytical', 'interpersonal', 'leadership']
        
        for category in categories:
            # Low score (0-40)
            ReportParagraphMapping.objects.get_or_create(
                category=category,
                min_score=0,
                max_score=40,
                defaults={
                    'title': f'Developing {category.title()} Skills',
                    'content': f'Your {category} skills are in the early stages of development. This is a great opportunity to focus on building a strong foundation.',
                    'recommendations': f'Consider taking courses and practicing {category} activities regularly.'
                }
            )
            
            # Medium score (41-70)
            ReportParagraphMapping.objects.get_or_create(
                category=category,
                min_score=41,
                max_score=70,
                defaults={
                    'title': f'Moderate {category.title()} Skills',
                    'content': f'You have a solid foundation in {category} skills with room for growth.',
                    'recommendations': f'Continue practicing and seek advanced opportunities in {category}.'
                }
            )
            
            # High score (71-100)
            ReportParagraphMapping.objects.get_or_create(
                category=category,
                min_score=71,
                max_score=100,
                defaults={
                    'title': f'Strong {category.title()} Skills',
                    'content': f'You demonstrate excellent {category} capabilities.',
                    'recommendations': f'Consider mentoring others and taking on leadership roles in {category}.'
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created default report mappings'))
