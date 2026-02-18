from rest_framework import serializers
from .models import Question, Test, TestQuestion, Attempt, Profile


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'dimension', 'weight']


class TestQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = TestQuestion
        fields = ['id', 'question', 'order']


class TestSerializer(serializers.ModelSerializer):
    test_questions = TestQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'duration_minutes', 'is_active', 'test_questions']


class AttemptSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source='test.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Attempt
        fields = ['id', 'user', 'user_username', 'test', 'test_name', 'status', 
                 'started_at', 'completed_at', 'answers', 'dimension_scores', 
                 'total_score', 'top_dimensions', 'pdf_report_file']
        read_only_fields = ['user', 'started_at', 'completed_at', 'dimension_scores', 
                           'total_score', 'top_dimensions', 'pdf_report_file']


class SubmitAttemptSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.IntegerField(min_value=1, max_value=5),
        help_text="Dictionary mapping question_id (as string) to answer value (1-5)"
    )
