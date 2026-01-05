from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Exam, Question, Submission, Answer

User = get_user_model()


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question_text", "question_type", "marks", "order"]
        read_only_fields = ["id"]


class ExamListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "course",
            "duration_minutes",
            "metadata",
            "created_at",
            "question_count",
        ]
        read_only_fields = ["id", "created_at"]
    
    def get_question_count(self, obj: Exam) -> int:
        """Return the number of questions in the exam."""
        return obj.questions.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "course",
            "duration_minutes",
            "metadata",
            "created_at",
            "questions",
        ]
        read_only_fields = ["id", "created_at"]


class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.CharField()
    student_answer = serializers.CharField(allow_blank=True)
    
    def validate_question_id(self, value):
        """Validate that the question exists."""
        try:
            Question.objects.get(id=value)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question not found.")
        return value


class SubmissionCreateSerializer(serializers.ModelSerializer):
    answers = AnswerSubmissionSerializer(many=True)
    
    class Meta:
        model = Submission
        fields = ["answers"]
    
    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer is required.")
        
        question_ids = [answer.get("question_id") for answer in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("Duplicate question IDs are not allowed.")
        
        return value
    
    def validate(self, attrs):
        exam = self.context.get("exam")
        if exam and "answers" in attrs:
            exam_question_ids = set(exam.questions.values_list("id", flat=True))
            submitted_question_ids = {answer.get("question_id") for answer in attrs["answers"]}
            
            invalid_questions = submitted_question_ids - exam_question_ids
            if invalid_questions:
                raise serializers.ValidationError({
                    "answers": f"Questions {invalid_questions} do not belong to this exam."
                })
            
            missing_questions = exam_question_ids - submitted_question_ids
            if missing_questions:
                raise serializers.ValidationError({
                    "answers": f"All questions must be answered. Missing: {missing_questions}"
                })
        
        return attrs
    
    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        exam = self.context["exam"]
        student = self.context["request"].user
        
        submission, created = Submission.objects.get_or_create(
            student=student,
            exam=exam,
            defaults={}
        )
        
        if not created:
            raise serializers.ValidationError(
                "You have already submitted this exam."
            )
        
        for answer_data in answers_data:
            question = Question.objects.get(id=answer_data["question_id"])
            Answer.objects.create(
                submission=submission,
                question=question,
                student_answer=answer_data["student_answer"]
            )
        
        return submission


class AnswerDetailSerializer(serializers.ModelSerializer):
    question_id = serializers.CharField(source="question.id", read_only=True)
    question_text = serializers.CharField(source="question.question_text", read_only=True)
    question_type = serializers.CharField(source="question.question_type", read_only=True)
    max_marks = serializers.IntegerField(source="question.marks", read_only=True)
    
    class Meta:
        model = Answer
        fields = [
            "question_id",
            "question_text",
            "question_type",
            "student_answer",
            "awarded_marks",
            "max_marks",
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    exam_course = serializers.CharField(source="exam.course", read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)
    answers = AnswerDetailSerializer(many=True, read_only=True)
    percentage_score = serializers.FloatField(read_only=True)
    is_graded = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            "id",
            "student_username",
            "exam_title",
            "exam_course",
            "submitted_at",
            "graded_at",
            "score",
            "max_score",
            "percentage_score",
            "is_graded",
            "answers",
        ]
        read_only_fields = [
            "id",
            "submitted_at",
            "graded_at",
            "score",
            "max_score",
        ]


class SubmissionListSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    exam_course = serializers.CharField(source="exam.course", read_only=True)
    percentage_score = serializers.FloatField(read_only=True)
    is_graded = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            "id",
            "exam_title",
            "exam_course",
            "submitted_at",
            "graded_at",
            "score",
            "max_score",
            "percentage_score",
            "is_graded",
        ]
        read_only_fields = ["id", "submitted_at", "graded_at", "score", "max_score"]
