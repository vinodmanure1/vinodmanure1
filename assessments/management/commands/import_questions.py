import csv
from django.core.management.base import BaseCommand
from assessments.models import Question


class Command(BaseCommand):
    help = 'Import questions from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Delete existing questions
                Question.objects.all().delete()
                self.stdout.write(self.style.WARNING('Deleted existing questions'))
                
                imported_count = 0
                for row in reader:
                    Question.objects.create(
                        text=row['text'],
                        category=row['category'],
                        weight=int(row.get('weight', 1))
                    )
                    imported_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {imported_count} questions')
                )
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file}')
            )
        except KeyError as e:
            self.stdout.write(
                self.style.ERROR(f'Missing required column in CSV: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing questions: {e}')
            )
