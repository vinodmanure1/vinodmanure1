from django.contrib import admin
from .models import Career, Assessment, Question, Answer, Result


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'average_salary', 'growth_rate', 'created_at']
    list_filter = ['industry', 'created_at']
    search_fields = ['name', 'description', 'industry']
    ordering = ['name']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ['text', 'career', 'score', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'order']
    show_change_link = True


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_minutes', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'text', 'question_type', 'order', 'created_at']
    list_filter = ['question_type', 'assessment']
    search_fields = ['text']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'text', 'career', 'score', 'order']
    list_filter = ['career', 'question__assessment']
    search_fields = ['text']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['get_user_display', 'assessment', 'recommended_career', 'completed_at']
    list_filter = ['assessment', 'recommended_career', 'completed_at']
    search_fields = ['student_name', 'student_email', 'user__username']
    readonly_fields = ['score_details', 'responses', 'completed_at']

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username
        return obj.student_name or "Anonymous"
    get_user_display.short_description = 'User'
