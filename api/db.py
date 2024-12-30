from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Index, text
import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import time

from env import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
import datetime
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


def connect_db(trial: int):
    if trial >= 30:
        print("connection refused")
        return None, None, None
    try:
        engine = create_engine(
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4')
        SessionLocal = sessionmaker(bind=engine)
        Base = declarative_base()
        return engine, SessionLocal, Base
    except Exception as e:
        time.sleep(1)
        print(e)
        return connect_db(trial + 1)


engine, SessionLocal, Base = connect_db(0)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String)
    user_id = Column(String)
    question = Column(String)
    thread_ts = Column(String)
    tags = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now(JST))


class QuestionCreate(BaseModel):
    channel_id: str
    user_id: str
    question: str
    thread_ts: str
    tags: str


def create_question(question: QuestionCreate, db: Session = get_db()):
    db.add(Question(**question.dict()))
    db.commit()
    db.refresh(question)
    return question


RELEVANCE_THRESHOLD = 0.5


def get_question_by_tags(tags: str, limit: int = 5, db: Session = get_db()):
    sql = text("""
               SELECT *, MATCH(tags) AGAINST(:tags IN BOOLEAN MODE WITH QUERY EXPANSION) as relevance
               FROM questions
               WHERE MATCH(tags) AGAINST(:tags IN BOOLEAN MODE WITH QUERY EXPANSION)
               ORDER BY  DESC
               LIMIT :limit
               """)
    result = db.execute(sql, {"tags": tags, "limit": limit})
    return result.fetchall()


def get_question_by_question(question: str, limit: int = 5, db: Session = get_db()):
    sql = text("""
               SELECT *, MATCH(question) AGAINST(:question IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION) as relevance
               FROM questions
               WHERE MATCH(question) AGAINST(:question IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION)
               ORDER BY  DESC
               LIMIT :limit
               """)
    result = db.execute(sql, {"question": question, "limit": limit})
    return result.fetchall()
