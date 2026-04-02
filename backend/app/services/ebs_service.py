import json
import os
import re
from functools import lru_cache
from typing import List, Dict, Any, Optional
from app.config import DATA_DIR
import logging

logger = logging.getLogger(__name__)

EBS_DATA_PATH = DATA_DIR / "ebs_courses.json"

class EBSService:
    def __init__(self):
        self.courses = []
        self._load_data()

    def _load_data(self):
        if EBS_DATA_PATH.exists():
            try:
                with open(EBS_DATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.courses = data.get("courses", [])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to load EBS data: {e}")

    def recommend(self, level: Optional[str] = None, topics: Optional[List[str]] = None, 
                  difficulty: Optional[str] = None, limit: int = 6) -> List[Dict[str, Any]]:
        """Score-based recommendation"""
        scored = []
        for course in self.courses:
            score = 0
            
            # Level: direct match (10)
            if level and course.get("level") == level:
                score += 10
            elif level:
                score -= 5
                
            # Topic: partial match (5)
            if topics:
                course_topics = course.get("topics", [])
                for topic in topics:
                    if any(topic.lower() in ct.lower() for ct in course_topics):
                        score += 5
            
            # Difficulty: Match (3), adjacent (1)
            if difficulty and course.get("difficulty") == difficulty:
                score += 3
            
            score += course.get("rating", 0) * 0.5
            
            if score > 0:
                scored.append({"course": course, "score": score})
                
        scored.sort(key=lambda x: x["score"], reverse=True)
        return [item["course"] for item in scored[:limit]]

    def get_all(self, level: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        if level:
            filtered = [c for c in self.courses if c.get("level") == level]
        else:
            filtered = self.courses
        return filtered[skip:skip+limit]

    def search(self, query: str) -> List[Dict[str, Any]]:
        # A simple TF-IDF like approach could work, but here we do simple regex term matching 
        # improved by checking multiple terms
        query_terms = query.lower().split()
        results = []
        for course in self.courses:
            searchable_text = " ".join([
                course.get("title", ""), course.get("description", ""),
                course.get("teacher", ""), course.get("subject", ""),
                " ".join(course.get("topics", []))
            ]).lower()
            
            # Match if all terms are found
            if all(term in searchable_text for term in query_terms):
                results.append(course)
        return results
