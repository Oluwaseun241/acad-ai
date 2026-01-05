
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Exam, Question, Submission, Answer
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ExamListSerializer,
    ExamDetailSerializer,
    SubmissionCreateSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)
from .grading import get_grading_service


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return all exams, ordered by creation date."""
        return Exam.objects.prefetch_related("questions").all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "retrieve":
            return ExamDetailSerializer
        return ExamListSerializer
    
    @extend_schema(
        summary="List all available exams",
        description="Retrieve a list of all available exams with basic information.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve exam details",
        description="Retrieve detailed information about a specific exam including all questions.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Submit exam answers",
        description=(
            "Submit answers for an exam. This endpoint validates that all questions "
            "are answered and creates a submission. Grading is performed automatically."
        ),
        request=SubmissionCreateSerializer,
        responses={201: SubmissionDetailSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="submit",
        serializer_class=SubmissionCreateSerializer,
    )
    def submit(self, request, pk=None):
        exam = self.get_object()
        
        existing_submission = Submission.objects.filter(
            student=request.user,
            exam=exam
        ).first()
        
        if existing_submission:
            return Response(
                {"detail": "You have already submitted this exam."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmissionCreateSerializer(
            data=request.data,
            context={"request": request, "exam": exam}
        )
        
        if serializer.is_valid():
            submission = serializer.save()
            self._grade_submission(submission)
            detail_serializer = SubmissionDetailSerializer(submission)
            return Response(
                detail_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _grade_submission(self, submission: Submission):
        grading_service = get_grading_service()
        answers = submission.answers.select_related("question").all()
        
        total_score = 0.0
        max_score = 0.0
        
        for answer in answers:
            question = answer.question
            max_score += question.marks
            
            grading_result = grading_service.grade_answer(
                student_answer=answer.student_answer,
                expected_answer=question.expected_answer,
                question_type=question.question_type,
                max_marks=question.marks
            )
            
            answer.awarded_marks = grading_result["awarded_marks"]
            answer.save()
            
            total_score += grading_result["awarded_marks"]
        
        submission.score = round(total_score, 2)
        submission.max_score = max_score
        submission.graded_at = timezone.now()
        submission.save()


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Submission.objects.filter(
            student=self.request.user
        ).select_related(
            "exam",
            "student"
        ).prefetch_related(
            "answers__question"
        ).order_by("-submitted_at")
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "retrieve":
            return SubmissionDetailSerializer
        return SubmissionListSerializer
    
    @extend_schema(
        summary="List user's submissions",
        description="Retrieve a list of all submissions made by the authenticated user.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Retrieve submission details",
        description=(
            "Retrieve detailed information about a specific submission including "
            "all answers and grading results. Users can only view their own submissions."
        ),
        parameters=[
            OpenApiParameter(
                name="id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Submission ID (ULID)",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        submission = self.get_object()
        
        if submission.student != request.user:
            return Response(
                {"detail": "You do not have permission to view this submission."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().retrieve(request, *args, **kwargs)
