from django.contrib import admin
from .models import Question, Test, TestQuestion, Attempt, Profile, ReportParagraphMapping


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1
    fields = ['question', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_preview', 'dimension', 'weight', 'order', 'is_active']
    list_filter = ['dimension', 'is_active']
    search_fields = ['text', 'dimension']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'id']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_minutes', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    inlines = [TestQuestionInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'test', 'status', 'total_score', 'started_at', 'completed_at']
    list_filter = ['status', 'test', 'started_at']
    search_fields = ['user__username', 'test__title']
    readonly_fields = ['started_at', 'scores', 'answers']
    
    def has_add_permission(self, request):
        return False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'grade', 'phone']
    search_fields = ['user__username', 'full_name', 'phone']


@admin.register(ReportParagraphMapping)
class ReportParagraphMappingAdmin(admin.ModelAdmin):
    list_display = ['dimension', 'score_min', 'score_max']
    list_filter = ['dimension']
    ordering = ['dimension', 'score_min']

