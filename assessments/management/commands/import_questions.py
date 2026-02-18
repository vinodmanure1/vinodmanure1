"""
Management command to import questions from CSV file.

Usage: python manage.py import_questions <csv_file_path>
"""
import csv
from django.core.management.base import BaseCommand, CommandError
from assessments.models import Question


class Command(BaseCommand):
    help = 'Import questions from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing questions before importing',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear = options['clear']
        
        if clear:
            count = Question.objects.count()
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing questions'))
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                created_count = 0
                for row in reader:
                    try:
                        Question.objects.create(
                            text=row.get('text', '').strip(),
                            dimension=row.get('dimension', 'analytical').strip(),
                            weight=int(row.get('weight', 1)),
                            order=int(row.get('order', 0)),
                            is_active=row.get('is_active', 'True').strip().lower() == 'true'
                        )
                        created_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error creating question: {e}')
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {created_count} questions')
                )
                
        except FileNotFoundError:
            raise CommandError(f'CSV file "{csv_file}" not found')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')
