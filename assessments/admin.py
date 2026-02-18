"""
Admin configuration for assessments app.
"""
from django.contrib import admin
from .models import Question, Test, TestQuestion, Attempt, Profile, ReportParagraphMapping


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'category', 'difficulty', 'correct_answer']
    list_filter = ['category', 'difficulty']
    search_fields = ['question_text', 'category']


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1
    autocomplete_fields = ['question']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    inlines = [TestQuestionInline]


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ['test', 'question', 'order']
    list_filter = ['test']
    search_fields = ['test__title', 'question__question_text']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'grade_level', 'school', 'created_at']
    list_filter = ['grade_level', 'created_at']
    search_fields = ['full_name', 'email', 'school']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'test', 'started_at', 'completed_at', 'has_report']
    list_filter = ['test', 'started_at', 'completed_at']
    search_fields = ['student_name', 'student_email']
    readonly_fields = ['started_at', 'completed_at', 'scores']
    
    def has_report(self, obj):
        return bool(obj.report_pdf)
    has_report.boolean = True
    has_report.short_description = 'Report Generated'


@admin.register(ReportParagraphMapping)
class ReportParagraphMappingAdmin(admin.ModelAdmin):
    list_display = ['category', 'min_score', 'max_score']
    list_filter = ['category']
    search_fields = ['category', 'paragraph_text']
