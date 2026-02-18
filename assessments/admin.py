from django.contrib import admin
from .models import Question, StudentResponse, CareerRecommendation


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview', 'category', 'weight')
    list_filter = ('category',)
    search_fields = ('text',)
    
    def text_preview(self, obj):
        return obj.text[:100]
    text_preview.short_description = 'Question Text'


@admin.register(StudentResponse)
class StudentResponseAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'student_email', 'question_preview', 'rating', 'created_at')
    list_filter = ('rating', 'question__category', 'created_at')
    search_fields = ('student_name', 'student_email')
    date_hierarchy = 'created_at'
    
    def question_preview(self, obj):
        return f"{obj.question.category}: {obj.question.text[:50]}"
    question_preview.short_description = 'Question'


@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'student_email', 'recommended_career', 'created_at')
    list_filter = ('recommended_career', 'created_at')
    search_fields = ('student_name', 'student_email', 'recommended_career')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
