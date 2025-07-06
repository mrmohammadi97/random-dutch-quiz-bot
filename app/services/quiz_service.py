import random
import json
import unicodedata
from num2words import num2words
from app.services.time_service import TimeService
from app.services.user_service import UserService
from app.models.quiz_session import QuizSession
from app.config.settings import settings


class QuizService:
    def __init__(self):
        self.time_service = TimeService()
        self.user_service = UserService()

    def generate_number_question(self, user_id: int):
        # Define probability ranges
        rand = random.random()

        # Try 60% < 100
        if rand < 0.6 and settings.NUMBER_RANGE_MIN <= 99:
            max_range = min(99, settings.NUMBER_RANGE_MAX)
            number = random.randint(settings.NUMBER_RANGE_MIN, max_range)

        # Try 30% 100-1000
        elif rand < 0.9 and settings.NUMBER_RANGE_MAX >= 100:
            min_range = max(100, settings.NUMBER_RANGE_MIN)
            max_range = min(1000, settings.NUMBER_RANGE_MAX)
            number = random.randint(min_range, max_range)

        # Try 10% > 1000, fallback to any valid range
        elif settings.NUMBER_RANGE_MAX > 1000:
            min_range = max(1001, settings.NUMBER_RANGE_MIN)
            number = random.randint(min_range, settings.NUMBER_RANGE_MAX)

        else:
            # Fallback: generate from any available range
            number = random.randint(settings.NUMBER_RANGE_MIN, settings.NUMBER_RANGE_MAX)

        correct_answer = num2words(number, lang='nl')

        question_data = {'number': number}
        self.user_service.increment_question_count(user_id, 'numbers')

        return {
            'type': 'numbers',
            'display': str(number),
            'answer': correct_answer,
            'data': question_data
        }

    def generate_time_question(self, user_id: int):
        hour = random.randint(1, 12)
        minute = random.choice(settings.TIME_MINUTES)

        time_str = f"{hour:02d}:{minute:02d}"
        correct_answer = self.time_service.time_to_dutch(hour, minute)

        question_data = {'hour': hour, 'minute': minute}
        self.user_service.increment_question_count(user_id, 'time')

        return {
            'type': 'time',
            'display': time_str,
            'answer': correct_answer,
            'data': question_data
        }

    def check_answer(self, user_answer: str, correct_answer: str) -> bool:
        return self._normalize_answer(user_answer) == self._normalize_answer(correct_answer)

    def _normalize_answer(self, text: str) -> str:
        """Normalize text by removing accents and converting to lowercase"""
        if not text:
            return ""

        # Convert to lowercase and strip
        text = text.lower().strip()

        # Remove accents and diacritics
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')

        # Additional specific replacements for Dutch
        replacements = {
            'ë': 'e',
            'ï': 'i',
            'ö': 'o',
            'ü': 'u',
            'é': 'e',
            'è': 'e',
            'ê': 'e',
            'á': 'a',
            'à': 'a',
            'â': 'a',
            'ó': 'o',
            'ò': 'o',
            'ô': 'o',
            'ú': 'u',
            'ù': 'u',
            'û': 'u',
            'í': 'i',
            'ì': 'i',
            'î': 'i'
        }

        for accented, plain in replacements.items():
            text = text.replace(accented, plain)

        return text

    def save_quiz_session(self, user_id: int, quiz_data: dict, user_answer: str, is_correct: bool, attempts: int):
        session = QuizSession(
            user_id=user_id,
            quiz_type=quiz_data['type'],
            question_data=json.dumps(quiz_data['data']),
            answer=quiz_data['answer'],
            user_answer=user_answer,
            is_correct=is_correct,
            attempts=attempts
        )
        db = self.user_service.db
        db.add(session)
        db.commit()