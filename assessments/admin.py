from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Question, Test, TestQuestion, Attempt, Profile, ReportParagraphMapping


class QuestionResource(resources.ModelResource):
    """Resource for importing/exporting Question data."""
    class Meta:
        model = Question
        fields = ('id', 'text', 'dimension', 'weight')


class TestQuestionInline(admin.TabularInline):
    """Inline for TestQuestion in Test admin."""
    model = TestQuestion
    extra = 1
    autocomplete_fields = ['question']


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    """Admin for Question model with import/export."""
    resource_class = QuestionResource
    list_display = ('id', 'text_preview', 'dimension', 'weight', 'created_at')
    list_filter = ('dimension', 'created_at')
    search_fields = ('text', 'dimension')
    ordering = ('dimension', 'id')
    
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Question Text'


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    """Admin for Test model."""
    list_display = ('id', 'name', 'duration_minutes', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    inlines = [TestQuestionInline]
    ordering = ('-created_at',)


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    """Admin for TestQuestion model."""
    list_display = ('id', 'test', 'question_preview', 'order')
    list_filter = ('test',)
    search_fields = ('test__name', 'question__text')
    ordering = ('test', 'order')
    
    def question_preview(self, obj):
        return obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = 'Question'


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    """Admin for Attempt model."""
    list_display = ('id', 'user', 'test', 'status', 'total_score', 'started_at', 'completed_at')
    list_filter = ('status', 'test', 'started_at')
    search_fields = ('user__username', 'test__name')
    readonly_fields = ('started_at', 'completed_at', 'dimension_scores', 'total_score', 'top_dimensions')
    ordering = ('-started_at',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin for Profile model."""
    list_display = ('id', 'user', 'full_name', 'phone', 'created_at')
    search_fields = ('user__username', 'full_name', 'phone')
    ordering = ('-created_at',)


@admin.register(ReportParagraphMapping)
class ReportParagraphMappingAdmin(admin.ModelAdmin):
    """Admin for ReportParagraphMapping model."""
    list_display = ('id', 'dimension', 'score_range_min', 'score_range_max', 'paragraph_preview')
    list_filter = ('dimension',)
    search_fields = ('dimension', 'paragraph_text')
    ordering = ('dimension', 'score_range_min')
    
    def paragraph_preview(self, obj):
        return obj.paragraph_text[:100] + '...' if len(obj.paragraph_text) > 100 else obj.paragraph_text
    paragraph_preview.short_description = 'Paragraph Text'
