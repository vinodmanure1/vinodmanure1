from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Question, Test, TestQuestion, Attempt, Profile, ReportParagraphMapping


class QuestionResource(resources.ModelResource):
    """Resource for importing/exporting Questions"""
    class Meta:
        model = Question
        fields = ('id', 'text', 'dimension', 'weight')


class TestQuestionInline(admin.TabularInline):
    """Inline for managing test questions within Test admin"""
    model = TestQuestion
    extra = 1
    fields = ('question', 'order')
    ordering = ['order']


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    """Admin interface for Question model"""
    resource_class = QuestionResource
    list_display = ('id', 'dimension', 'text_preview', 'weight', 'created_at')
    list_filter = ('dimension', 'created_at')
    search_fields = ('text', 'dimension')
    ordering = ['dimension', 'id']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    """Admin interface for Test model"""
    list_display = ('id', 'title', 'duration_minutes', 'is_active', 'question_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [TestQuestionInline]
    ordering = ['-created_at']

    def question_count(self, obj):
        return obj.test_questions.count()
    question_count.short_description = 'Questions'


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    """Admin interface for TestQuestion model"""
    list_display = ('id', 'test', 'question_preview', 'order')
    list_filter = ('test',)
    search_fields = ('test__title', 'question__text')
    ordering = ['test', 'order']

    def question_preview(self, obj):
        return obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = 'Question'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model"""
    list_display = ('id', 'user', 'full_name', 'email', 'grade', 'school')
    search_fields = ('user__username', 'full_name', 'email', 'school')
    ordering = ['user__username']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    """Admin interface for Attempt model"""
    list_display = ('id', 'user', 'test', 'total_score', 'started_at', 'completed_at', 'has_pdf')
    list_filter = ('test', 'started_at', 'completed_at')
    search_fields = ('user__username', 'test__title')
    readonly_fields = ('answers', 'scores', 'total_score', 'top_dimensions', 'started_at')
    ordering = ['-started_at']

    def has_pdf(self, obj):
        return bool(obj.pdf_report_file)
    has_pdf.boolean = True
    has_pdf.short_description = 'PDF Generated'


@admin.register(ReportParagraphMapping)
class ReportParagraphMappingAdmin(admin.ModelAdmin):
    """Admin interface for ReportParagraphMapping model"""
    list_display = ('id', 'dimension', 'min_score', 'max_score', 'paragraph_preview')
    list_filter = ('dimension',)
    search_fields = ('dimension', 'paragraph_text')
    ordering = ['dimension', 'min_score']

    def paragraph_preview(self, obj):
        return obj.paragraph_text[:50] + '...' if len(obj.paragraph_text) > 50 else obj.paragraph_text
    paragraph_preview.short_description = 'Paragraph'
