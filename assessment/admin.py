"""
Admin configuration for the Assessment Engine models.
"""
from django.contrib import admin
from .models import Exam, Question, Submission, Answer


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "duration_minutes", "created_at"]
    list_filter = ["course", "created_at"]
    search_fields = ["title", "course"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ["awarded_marks"]
    fields = ["question", "student_answer", "awarded_marks"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "exam", "question_type", "marks", "order"]
    list_filter = ["question_type", "exam"]
    search_fields = ["question_text", "exam__title"]
    readonly_fields = ["id"]
    ordering = ["exam", "order"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "student",
        "exam",
        "submitted_at",
        "graded_at",
        "score",
        "max_score",
    ]
    list_filter = ["graded_at", "submitted_at", "exam"]
    search_fields = ["student__username", "exam__title"]
    readonly_fields = ["id", "submitted_at", "graded_at"]
    ordering = ["-submitted_at"]
    inlines = [AnswerInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("student", "exam")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["submission", "question", "awarded_marks"]
    list_filter = ["question__question_type"]
    search_fields = ["submission__student__username", "question__question_text"]
    readonly_fields = ["awarded_marks"]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("submission__student", "submission__exam", "question")
