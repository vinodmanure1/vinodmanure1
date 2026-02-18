"""
DRF Serializers for API endpoints
"""
from rest_framework import serializers
from .models import Question, Test, TestQuestion, Attempt, Profile


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'external_id', 'grade', 'topic', 'question_type', 
                 'question_text', 'options', 'weight', 'dimension']


class TestQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = TestQuestion
        fields = ['id', 'sequence', 'question']


class TestSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = ['id', 'name', 'grade', 'duration_minutes', 'created_at', 'questions_count']
    
    def get_questions_count(self, obj):
        return obj.test_questions.count()


class TestDetailSerializer(serializers.ModelSerializer):
    test_questions = TestQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Test
        fields = ['id', 'name', 'grade', 'duration_minutes', 'created_at', 'test_questions']


class AttemptSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source='test.name', read_only=True)
    
    class Meta:
        model = Attempt
        fields = ['id', 'test', 'test_name', 'user', 'started_at', 'completed_at', 
                 'raw_answers', 'scores', 'total_score', 'pdf_report_file']
        read_only_fields = ['user', 'started_at', 'completed_at', 'scores', 'total_score', 'pdf_report_file']


class AttemptSubmitSerializer(serializers.Serializer):
    """Serializer for submitting test answers"""
    test_id = serializers.IntegerField()
    answers = serializers.JSONField()


class AttemptAutosaveSerializer(serializers.Serializer):
    """Serializer for autosaving partial answers"""
    attempt_id = serializers.IntegerField()
    answers = serializers.JSONField()
