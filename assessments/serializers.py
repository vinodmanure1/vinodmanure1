from rest_framework import serializers
from .models import Question, Test, Attempt, Profile


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'dimension', 'weight', 'order']


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Test
        fields = ['id', 'title', 'description', 'duration_minutes', 'questions']


class AttemptSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Attempt
        fields = ['id', 'test', 'test_title', 'user_name', 'status', 'answers', 
                  'scores', 'total_score', 'started_at', 'completed_at', 'pdf_report_file']
        read_only_fields = ['scores', 'total_score', 'started_at', 'completed_at', 'pdf_report_file']


class AttemptSubmitSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.IntegerField(min_value=0, max_value=5),
        help_text="Dictionary mapping question_id to answer score (0-5)"
    )


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['username', 'full_name', 'phone', 'date_of_birth', 'grade']
