from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Profile, Question, Test, TestQuestion, Attempt, ReportParagraphMapping
from .services import import_questions_from_csv


class QuestionResource(resources.ModelResource):
    """Resource for importing/exporting questions"""
    class Meta:
        model = Question
        import_id_fields = ['external_id']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'grade', 'role']
    list_filter = ['role', 'grade']
    search_fields = ['user__username', 'user__email']


@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ['external_id', 'grade', 'topic', 'question_type', 'dimension', 'weight']
    list_filter = ['grade', 'question_type', 'dimension']
    search_fields = ['external_id', 'topic', 'question_text']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv_view), name='upload-csv'),
        ]
        return custom_urls + urls
    
    def upload_csv_view(self, request):
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            try:
                result = import_questions_from_csv(csv_file)
                return JsonResponse({
                    'success': True,
                    'message': f"Successfully imported {result['created']} questions, updated {result['updated']} questions."
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
        return render(request, 'admin/assessments/upload_csv.html')


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1
    autocomplete_fields = ['question']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'duration_minutes', 'created_at']
    list_filter = ['grade']
    search_fields = ['name']
    inlines = [TestQuestionInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'started_at', 'completed_at', 'total_score', 'is_completed']
    list_filter = ['test', 'completed_at']
    search_fields = ['user__username']
    readonly_fields = ['started_at', 'completed_at', 'raw_answers', 'scores', 'total_score']
    
    def is_completed(self, obj):
        return obj.is_completed
    is_completed.boolean = True


@admin.register(ReportParagraphMapping)
class ReportParagraphMappingAdmin(admin.ModelAdmin):
    list_display = ['dimension', 'score_range']
    list_filter = ['dimension']
    search_fields = ['dimension', 'score_range']

