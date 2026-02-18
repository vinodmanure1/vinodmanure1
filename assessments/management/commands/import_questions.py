"""
Management command to import questions from CSV file
Usage: python manage.py import_questions <csv_file_path>
"""
from django.core.management.base import BaseCommand
from assessments.services import import_questions_from_csv


class Command(BaseCommand):
    help = 'Import questions from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
    
    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            with open(csv_file_path, 'r') as f:
                result = import_questions_from_csv(f)
            
            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported {result['created']} questions, "
                f"updated {result['updated']} questions."
            ))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing questions: {str(e)}"))
