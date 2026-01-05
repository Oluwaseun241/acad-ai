import re
from typing import Dict, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class GradingService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2), min_df=1
        )

    def grade_answer(
        self,
        student_answer: str,
        expected_answer: str,
        question_type: str,
        max_marks: int,
    ) -> Dict[str, float]:
        """
        Grade a student's answer against the expected answer.

        Args:
            student_answer: The student's submitted answer
            expected_answer: The expected/correct answer
            question_type: Type of question (MCQ, SHORT, ESSAY)
            max_marks: Maximum marks for this question

        Returns:
            Dictionary with 'awarded_marks' and 'similarity_score' (0-1)
        """
        if not student_answer or not student_answer.strip():
            return {"awarded_marks": 0.0, "similarity_score": 0.0}

        student_answer = self._normalize_text(student_answer)
        expected_answer = self._normalize_text(expected_answer)

        if question_type == "MCQ":
            similarity = self._grade_mcq(student_answer, expected_answer)
        elif question_type == "SHORT":
            similarity = self._grade_short_answer(student_answer, expected_answer)
        else:  # ESSAY
            similarity = self._grade_essay(student_answer, expected_answer)

        awarded_marks = round(similarity * max_marks, 2)

        return {"awarded_marks": awarded_marks, "similarity_score": similarity}

    def _normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _grade_mcq(self, student_answer: str, expected_answer: str) -> float:
        if student_answer == expected_answer:
            return 1.0

        if expected_answer in student_answer:
            return 0.9

        if student_answer in expected_answer:
            return 0.7

        student_words = set(student_answer.split())
        expected_words = set(expected_answer.split())

        if not expected_words:
            return 0.0

        overlap = len(student_words & expected_words) / len(expected_words)
        return min(overlap, 0.5)

    def _grade_short_answer(self, student_answer: str, expected_answer: str) -> float:
        if student_answer == expected_answer:
            return 1.0

        student_words = set(student_answer.split())
        expected_words = set(expected_answer.split())

        if not expected_words:
            return 0.0

        keyword_overlap = len(student_words & expected_words) / len(expected_words)

        try:
            tfidf_similarity = self._calculate_tfidf_similarity(
                student_answer, expected_answer
            )
        except Exception:
            tfidf_similarity = 0.0

        combined_score = (0.4 * keyword_overlap) + (0.6 * tfidf_similarity)

        return min(combined_score, 1.0)

    def _grade_essay(self, student_answer: str, expected_answer: str) -> float:
        try:
            similarity = self._calculate_tfidf_similarity(
                student_answer, expected_answer
            )
        except Exception:
            student_words = set(student_answer.split())
            expected_words = set(expected_answer.split())

            if not expected_words:
                return 0.0

            similarity = len(student_words & expected_words) / len(expected_words)

        return similarity

    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity using TF-IDF vectors.

        Args:
            text1: First text to compare
            text2: Second text to compare

        Returns:
            Similarity score between 0 and 1
        """
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity = float(similarity_matrix[0][0])
            return max(0.0, min(1.0, similarity))
        except Exception:
            return 0.0


_grader_instance: Optional[GradingService] = None


def get_grading_service() -> GradingService:
    global _grader_instance
    if _grader_instance is None:
        _grader_instance = GradingService()
    return _grader_instance
