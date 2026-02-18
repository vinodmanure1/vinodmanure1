import csv
from django.core.management.base import BaseCommand
from assessments.models import Question


class Command(BaseCommand):
    help = 'Import questions from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                created_count = 0
                
                for row in reader:
                    # Skip empty rows
                    if not row.get('text'):
                        continue
                    
                    question, created = Question.objects.get_or_create(
                        text=row['text'],
                        defaults={
                            'category': row['category'],
                            'option_a': row['option_a'],
                            'option_b': row['option_b'],
                            'option_c': row['option_c'],
                            'option_d': row['option_d'],
                            'correct_answer': row['correct_answer'].upper()
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Created: {question.text[:50]}'))
                
                self.stdout.write(self.style.SUCCESS(f'\nTotal questions created: {created_count}'))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
