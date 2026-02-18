"""
Management command to import questions from CSV file.
"""
from django.core.management.base import BaseCommand
from assessments.utils import import_questions_from_csv


class Command(BaseCommand):
    help = 'Import questions from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing questions'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            with open(csv_file_path, 'rb') as csv_file:
                result = import_questions_from_csv(csv_file)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully imported {result["created"]} questions'
                    )
                )
                
                if result['errors']:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Encountered {len(result["errors"])} errors:'
                        )
                    )
                    for error in result['errors']:
                        self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
