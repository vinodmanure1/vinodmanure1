import csv
import json
import os
from django.core.management.base import BaseCommand
from assessments.models import Career, Assessment, Question, Answer


class Command(BaseCommand):
    help = 'Import seed data from CSV and JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--careers',
            type=str,
            help='Path to careers CSV file',
        )
        parser.add_argument(
            '--assessment',
            type=str,
            help='Path to assessment JSON file',
        )

    def handle(self, *args, **options):
        careers_file = options.get('careers')
        assessment_file = options.get('assessment')

        if careers_file:
            self.import_careers(careers_file)
        
        if assessment_file:
            self.import_assessment(assessment_file)
        
        if not careers_file and not assessment_file:
            # Import default seed data if no files specified
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            seed_dir = os.path.join(base_dir, '..', 'seed_data')
            
            default_careers = os.path.join(seed_dir, 'careers.csv')
            default_assessment = os.path.join(seed_dir, 'assessment.json')
            
            if os.path.exists(default_careers):
                self.import_careers(default_careers)
            
            if os.path.exists(default_assessment):
                self.import_assessment(default_assessment)

    def import_careers(self, filepath):
        """Import careers from CSV file"""
        self.stdout.write(f'Importing careers from {filepath}...')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                career, created = Career.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'description': row.get('description', ''),
                        'industry': row.get('industry', ''),
                        'average_salary': float(row['average_salary']) if row.get('average_salary') else None,
                        'growth_rate': float(row['growth_rate']) if row.get('growth_rate') else None,
                        'education_required': row.get('education_required', ''),
                    }
                )
                count += 1
                action = 'Created' if created else 'Updated'
                self.stdout.write(f'  {action}: {career.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} careers'))

    def import_assessment(self, filepath):
        """Import assessment with questions and answers from JSON file"""
        self.stdout.write(f'Importing assessment from {filepath}...')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create or update assessment
        assessment_data = data.get('assessment', {})
        assessment, created = Assessment.objects.update_or_create(
            title=assessment_data['title'],
            defaults={
                'description': assessment_data.get('description', ''),
                'duration_minutes': assessment_data.get('duration_minutes', 30),
                'is_active': assessment_data.get('is_active', True),
            }
        )
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'  {action} assessment: {assessment.title}')
        
        # Import questions
        questions_data = data.get('questions', [])
        for q_data in questions_data:
            question, created = Question.objects.update_or_create(
                assessment=assessment,
                order=q_data['order'],
                defaults={
                    'text': q_data['text'],
                    'question_type': q_data.get('question_type', 'MULTIPLE_CHOICE'),
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'    {action} question: {question.text[:50]}...')
            
            # Import answers
            for a_data in q_data.get('answers', []):
                career = None
                if a_data.get('career_name'):
                    try:
                        career = Career.objects.get(name=a_data['career_name'])
                    except Career.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'      Career not found: {a_data["career_name"]}')
                        )
                
                answer, created = Answer.objects.update_or_create(
                    question=question,
                    order=a_data['order'],
                    defaults={
                        'text': a_data['text'],
                        'career': career,
                        'score': a_data.get('score', 0),
                    }
                )
                
                action = 'Created' if created else 'Updated'
                self.stdout.write(f'      {action} answer: {answer.text[:40]}...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported assessment with {len(questions_data)} questions'))
