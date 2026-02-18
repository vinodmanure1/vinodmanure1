"""
Utility functions for assessments app.
"""
import csv
import io
from .models import Question


def import_questions_from_csv(csv_file):
    """
    Import questions from CSV file.
    
    Expected CSV format:
    text,dimension,weight
    
    Returns:
        Dictionary with 'created' count and 'errors' list
    """
    result = {
        'created': 0,
        'errors': []
    }
    
    try:
        # Read CSV file
        text_file = io.StringIO(csv_file.read().decode('utf-8'))
        reader = csv.DictReader(text_file)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Validate required fields
                if 'text' not in row or not row['text']:
                    result['errors'].append(f"Row {row_num}: Missing 'text' field")
                    continue
                
                if 'dimension' not in row or not row['dimension']:
                    result['errors'].append(f"Row {row_num}: Missing 'dimension' field")
                    continue
                
                # Get weight (default to 1.0)
                weight = float(row.get('weight', 1.0))
                
                # Create question
                Question.objects.create(
                    text=row['text'].strip(),
                    dimension=row['dimension'].strip(),
                    weight=weight
                )
                
                result['created'] += 1
                
            except Exception as e:
                result['errors'].append(f"Row {row_num}: {str(e)}")
        
    except Exception as e:
        result['errors'].append(f"Error reading CSV: {str(e)}")
    
    return result
