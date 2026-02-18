"""
Management command to seed initial data
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assessments.models import Question, Test, TestQuestion, ReportParagraphMapping, Profile
from assessments.services import import_questions_from_csv
import os
import json


class Command(BaseCommand):
    help = 'Seed initial data for development'
    
    def handle(self, *args, **options):
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            Profile.objects.create(user=admin, role='admin', grade=None)
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin123)'))
        
        # Create sample student if not exists
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user('student', 'student@example.com', 'student123')
            Profile.objects.create(user=student, role='student', grade=9)
            self.stdout.write(self.style.SUCCESS('Created student user (username: student, password: student123)'))
        
        # Import questions from CSV if exists
        csv_path = os.path.join('seed', 'question_bank_template.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as f:
                result = import_questions_from_csv(f)
            self.stdout.write(self.style.SUCCESS(
                f"Imported {result['created']} questions, updated {result['updated']} questions"
            ))
        else:
            self.stdout.write(self.style.WARNING(f"CSV file not found: {csv_path}"))
        
        # Create a sample test for grade 9
        if not Test.objects.filter(name='Grade 9 Career Assessment').exists():
            test = Test.objects.create(
                name='Grade 9 Career Assessment',
                grade=9,
                duration_minutes=45
            )
            
            # Add questions to test
            questions = Question.objects.filter(grade=9)[:20]
            for idx, question in enumerate(questions, start=1):
                TestQuestion.objects.create(
                    test=test,
                    question=question,
                    sequence=idx
                )
            
            self.stdout.write(self.style.SUCCESS(f"Created test with {questions.count()} questions"))
        
        # Load report paragraph mappings
        mappings_path = os.path.join('seed', 'report_paragraph_mappings.json')
        if os.path.exists(mappings_path):
            with open(mappings_path, 'r') as f:
                mappings = json.load(f)
            
            for mapping in mappings:
                ReportParagraphMapping.objects.update_or_create(
                    dimension=mapping['dimension'],
                    score_range=mapping['score_range'],
                    defaults={
                        'student_paragraph': mapping['student_paragraph'],
                        'parent_paragraph': mapping['parent_paragraph'],
                    }
                )
            
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(mappings)} report paragraph mappings"))
        else:
            self.stdout.write(self.style.WARNING(f"Mappings file not found: {mappings_path}"))
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed!'))
