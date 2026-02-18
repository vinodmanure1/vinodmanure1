from django.contrib import admin
from .models import Question, Test, TestQuestion, Attempt, Profile, ReportParagraphMapping


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category', 'correct_answer', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['text', 'category']
    ordering = ['category', '-created_at']


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1
    autocomplete_fields = ['question']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_minutes', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [TestQuestionInline]
    ordering = ['-created_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'email', 'phone', 'created_at']
    search_fields = ['full_name', 'email', 'user__username']
    ordering = ['-created_at']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'status', 'total_score', 'percentage', 'started_at', 'completed_at']
    list_filter = ['status', 'test', 'started_at']
    search_fields = ['user__username', 'test__name']
    readonly_fields = ['answers', 'scores', 'total_score', 'percentage']
    ordering = ['-started_at']


@admin.register(ReportParagraphMapping)
class ReportParagraphMappingAdmin(admin.ModelAdmin):
    list_display = ['category', 'min_score', 'max_score', 'title']
    list_filter = ['category']
    search_fields = ['category', 'title', 'content']
    ordering = ['category', 'min_score']
