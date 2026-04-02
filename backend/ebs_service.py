"""
EBS Course Recommendation Service.
Loads EBS course data and provides filtered recommendations.
"""
import json
import os
from pathlib import Path


DATA_PATH = Path(__file__).parent / "data" / "ebs_courses.json"


class EBSService:
    def __init__(self):
        self.courses: list[dict] = []
        self._load_data()

    def _load_data(self):
        if DATA_PATH.exists():
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.courses = data.get("courses", [])

    def recommend(
        self,
        level: str | None = None,
        topics: list[str] | None = None,
        difficulty: str | None = None,
        limit: int = 6,
    ) -> list[dict]:
        """
        Recommend EBS courses based on student profile.
        Returns scored and sorted list of matching courses.
        """
        scored = []

        for course in self.courses:
            score = 0

            # Level matching (high priority)
            if level and course.get("level") == level:
                score += 10
            elif level and course.get("level") != level:
                # Still include if topics overlap, but lower score
                score -= 5

            # Topic matching
            if topics:
                course_topics = [t.lower() for t in course.get("topics", [])]
                for topic in topics:
                    topic_lower = topic.lower()
                    for ct in course_topics:
                        if topic_lower in ct or ct in topic_lower:
                            score += 5

            # Difficulty matching
            if difficulty and course.get("difficulty") == difficulty:
                score += 3
            elif difficulty:
                # Adjacent difficulty still gets some score
                diff_order = ["beginner", "intermediate", "advanced"]
                if difficulty in diff_order and course.get("difficulty") in diff_order:
                    dist = abs(diff_order.index(difficulty) - diff_order.index(course["difficulty"]))
                    if dist == 1:
                        score += 1

            # Rating bonus
            score += course.get("rating", 0) * 0.5

            if score > 0:
                scored.append({"course": course, "score": score})

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)

        return [item["course"] for item in scored[:limit]]

    def get_all(self, level: str | None = None) -> list[dict]:
        """Get all courses, optionally filtered by level."""
        if level:
            return [c for c in self.courses if c.get("level") == level]
        return self.courses

    def get_by_id(self, course_id: str) -> dict | None:
        for c in self.courses:
            if c.get("id") == course_id:
                return c
        return None

    def search(self, query: str) -> list[dict]:
        """Full-text search across course titles, descriptions, topics."""
        query_lower = query.lower()
        results = []
        for course in self.courses:
            searchable = " ".join([
                course.get("title", ""),
                course.get("description", ""),
                course.get("teacher", ""),
                course.get("subject", ""),
                " ".join(course.get("topics", [])),
            ]).lower()

            if query_lower in searchable:
                results.append(course)

        return results


# Singleton
ebs_service = EBSService()
