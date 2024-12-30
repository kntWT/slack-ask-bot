from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, text
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
import datetime
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
        meta = MetaData()
        conn = engine.connect()
        return engine, meta, conn
    except Exception as e:
        time.sleep(1)
        print(e)
        return connect_db(trial + 1)


engine, meta, conn = connect_db(0)


questions_table = Table(
    'questions', meta,
    Column('id', Integer, primary_key=True),
    Column('channel_id', String(255)),
    Column('user_id', String(255)),
    Column('question', String(255)),
    Column('thread_ts', String(255)),
    Column('tags', String(255)),
    Column('created_at', DateTime, default=datetime.datetime.now(JST))
)
meta.create_all(engine)


class QuestionCreate(BaseModel):
    channel_id: str
    user_id: str
    question: str
    thread_ts: str
    tags: str


def create_question(question: QuestionCreate):
    conn.execute(questions_table.insert().values(
        **question
    ))
    conn.commit()
    return question


RELEVANCE_THRESHOLD = 0.5


def get_question_by_tags(tags: str, limit: int = 5):
    sql = text("""
               SELECT *, MATCH(tags) AGAINST(:tags IN BOOLEAN MODE WITH QUERY EXPANSION) as relevance
               FROM questions
               WHERE MATCH(tags) AGAINST(:tags IN BOOLEAN MODE WITH QUERY EXPANSION)
               ORDER BY  DESC
               LIMIT :limit
               """)
    result = conn.execute(sql, {"tags": tags, "limit": limit})
    return result.fetchall()


def get_question_by_question(question: str, limit: int = 5):
    sql = text("""
               SELECT *, MATCH(question) AGAINST(:question IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION) as relevance
               FROM questions
               WHERE MATCH(question) AGAINST(:question IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION)
               ORDER BY  DESC
               LIMIT :limit
               """)
    result = conn.execute(sql, {"question": question, "limit": limit})
    return result.fetchall()
