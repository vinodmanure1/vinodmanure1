"""
Management command to import questions from CSV file.
"""
import csv
from django.core.management.base import BaseCommand, CommandError
from assessments.models import Question


class Command(BaseCommand):
    help = 'Import questions from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing questions before importing',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear_existing = options['clear']

        if clear_existing:
            count = Question.objects.count()
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing questions'))

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                questions_created = 0
                
                for row in reader:
                    # Expected columns: text, dimension, weight
                    text = row.get('text', '').strip()
                    dimension = row.get('dimension', '').strip().lower()
                    weight = float(row.get('weight', 1.0))
                    
                    if not text or not dimension:
                        self.stdout.write(self.style.WARNING(f'Skipping invalid row: {row}'))
                        continue
                    
                    # Validate dimension
                    valid_dimensions = [choice[0] for choice in Question.DIMENSION_CHOICES]
                    if dimension not in valid_dimensions:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Invalid dimension "{dimension}" for question: {text[:50]}. '
                                f'Valid options: {", ".join(valid_dimensions)}'
                            )
                        )
                        continue
                    
                    question = Question.objects.create(
                        text=text,
                        dimension=dimension,
                        weight=weight
                    )
                    questions_created += 1
                    
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {questions_created} questions')
                )
                
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file}" does not exist')
        except Exception as e:
            raise CommandError(f'Error importing questions: {str(e)}')
