from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.user import Base


class QuizSession(Base):
    __tablename__ = 'quiz_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    quiz_type = Column(String(50))  # 'numbers' or 'time'
    question_data = Column(String(255))  # JSON string of question
    answer = Column(String(255))
    user_answer = Column(String(255))
    is_correct = Column(Boolean)
    attempts = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")