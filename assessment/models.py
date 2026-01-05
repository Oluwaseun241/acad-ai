import ulid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


def generate_ulid_as_string():
    """Generate a ULID string for use as primary key."""
    return str(ulid.new())


class Exam(models.Model):
    """Represents an exam/assessment."""

    id = models.CharField(
        primary_key=True, default=generate_ulid_as_string, editable=False, max_length=26
    )
    title = models.CharField(max_length=255, db_index=True)
    course = models.CharField(max_length=255, db_index=True)
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["course", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.course})"


class Question(models.Model):
    """Represents a question within an exam."""

    QUESTION_TYPES = (
        ("MCQ", "Multiple Choice Question"),
        ("SHORT", "Short Answer"),
        ("ESSAY", "Essay"),
    )

    id = models.CharField(
        primary_key=True, default=generate_ulid_as_string, editable=False, max_length=26
    )
    exam = models.ForeignKey(
        Exam, related_name="questions", on_delete=models.CASCADE, db_index=True
    )
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    expected_answer = models.TextField()
    marks = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["exam", "order"]),
        ]

    def __str__(self):
        return f"{self.exam.title} - Q{self.order + 1}"


class Submission(models.Model):
    """Represents a student's submission for an exam."""

    id = models.CharField(
        primary_key=True, default=generate_ulid_as_string, editable=False, max_length=26
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="submissions",
        on_delete=models.CASCADE,
        db_index=True,
    )
    exam = models.ForeignKey(
        Exam, related_name="submissions", on_delete=models.CASCADE, db_index=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    max_score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = [("student", "exam")]
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["student", "-submitted_at"]),
            models.Index(fields=["exam", "-submitted_at"]),
            models.Index(fields=["student", "exam", "-submitted_at"]),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

    @property
    def is_graded(self):
        return self.graded_at is not None

    @property
    def percentage_score(self):
        if self.score is not None and self.max_score and self.max_score > 0:
            return round((self.score / self.max_score) * 100, 2)
        return None


class Answer(models.Model):
    """Represents a student's answer to a specific question."""

    submission = models.ForeignKey(
        Submission, related_name="answers", on_delete=models.CASCADE, db_index=True
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_index=True)
    student_answer = models.TextField()
    awarded_marks = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    class Meta:
        unique_together = [("submission", "question")]
        indexes = [
            models.Index(fields=["submission", "question"]),
        ]

    def __str__(self):
        return f"{self.submission} - {self.question.id}"
