"""
Management command to import questions from CSV.
"""
import csv
from django.core.management.base import BaseCommand
from assessments.models import Question


class Command(BaseCommand):
    help = 'Import questions from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file with questions'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                created_count = 0
                
                for row in reader:
                    question, created = Question.objects.get_or_create(
                        question_text=row['question_text'],
                        defaults={
                            'option_a': row['option_a'],
                            'option_b': row['option_b'],
                            'option_c': row['option_c'],
                            'option_d': row['option_d'],
                            'correct_answer': row['correct_answer'].upper(),
                            'category': row['category'],
                            'difficulty': row.get('difficulty', 'Medium'),
                        }
                    )
                    
                    if created:
                        created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully imported {created_count} questions'
                    )
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing questions: {str(e)}')
            )
