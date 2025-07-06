from sqlalchemy.orm import Session
from app.models.user import User, SessionLocal
from app.models.quiz_session import QuizSession
from telegram import Update


class UserService:
    def __init__(self):
        self.db = SessionLocal()

    def get_or_create_user(self, update: Update) -> User:
        telegram_user = update.effective_user
        user = self.db.query(User).filter(User.telegram_id == telegram_user.id).first()

        if not user:
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def increment_question_count(self, user_id: int, quiz_type: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            if quiz_type == 'numbers':
                user.number_questions_count += 1
            elif quiz_type == 'time':
                user.time_questions_count += 1
            self.db.commit()

    def get_user_stats(self, telegram_id: int):
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            return {
                'number_questions': user.number_questions_count,
                'time_questions': user.time_questions_count,
                'total_questions': user.number_questions_count + user.time_questions_count
            }
        return None

    def close(self):
        self.db.close()