"""
Tests for CSV import functionality.
"""
import pytest
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from assessments.models import Question
from assessments.utils import import_questions_from_csv


@pytest.mark.django_db
class TestCSVImport:
    """Test CSV import functionality"""
    
    def test_import_valid_csv(self):
        """Test importing a valid CSV file"""
        csv_content = """text,dimension,weight
Question 1?,Technical,1.0
Question 2?,Leadership,1.5
Question 3?,Creative,2.0"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        result = import_questions_from_csv(csv_file)
        
        assert result['created'] == 3
        assert len(result['errors']) == 0
        
        # Verify questions were created
        assert Question.objects.count() == 3
        
        # Verify data
        q1 = Question.objects.get(text='Question 1?')
        assert q1.dimension == 'Technical'
        assert q1.weight == 1.0
        
        q2 = Question.objects.get(text='Question 2?')
        assert q2.dimension == 'Leadership'
        assert q2.weight == 1.5
    
    def test_import_csv_missing_weight(self):
        """Test importing CSV without weight column (should default to 1.0)"""
        csv_content = """text,dimension
Question A?,Technical
Question B?,Leadership"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        result = import_questions_from_csv(csv_file)
        
        assert result['created'] == 2
        
        # Verify default weight
        for question in Question.objects.all():
            assert question.weight == 1.0
    
    def test_import_csv_missing_required_field(self):
        """Test importing CSV with missing required fields"""
        csv_content = """text,dimension,weight
Question 1?,Technical,1.0
,Leadership,1.0
Question 3?,,1.0"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        result = import_questions_from_csv(csv_file)
        
        # Only the first question should be imported
        assert result['created'] == 1
        assert len(result['errors']) == 2
        assert Question.objects.count() == 1
    
    def test_import_empty_csv(self):
        """Test importing an empty CSV"""
        csv_content = """text,dimension,weight"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        result = import_questions_from_csv(csv_file)
        
        assert result['created'] == 0
        assert Question.objects.count() == 0
    
    def test_import_csv_with_whitespace(self):
        """Test that whitespace is stripped from imported data"""
        csv_content = """text,dimension,weight
  Question with spaces?  ,  Technical  ,1.0"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        result = import_questions_from_csv(csv_file)
        
        assert result['created'] == 1
        
        question = Question.objects.first()
        assert question.text == 'Question with spaces?'
        assert question.dimension == 'Technical'
    
    def test_import_csv_invalid_weight(self):
        """Test importing CSV with invalid weight value"""
        csv_content = """text,dimension,weight
Question 1?,Technical,invalid
Question 2?,Leadership,1.0"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        result = import_questions_from_csv(csv_file)
        
        # First question should fail, second should succeed
        assert result['created'] == 1
        assert len(result['errors']) == 1
        assert Question.objects.count() == 1
        
        question = Question.objects.first()
        assert question.text == 'Question 2?'
