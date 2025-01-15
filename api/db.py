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
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4',
            pool_recycle=3600,  # 1時間ごとに再接続)
            pool_pre_ping=True  # 接続が有効か確認する
        )
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
    Column('thread_ts', String(255)),
    Column('question', String(255)),
    Column('user_id', String(255)),
    Column('dm_id', String(255)),
    Column('tags', String(255)),
    Column('created_at', DateTime, default=datetime.datetime.now(JST))
)
meta.create_all(engine)


class QuestionCreate(BaseModel):
    channel_id: str
    user_id: str
    dm_id: str
    question: str
    thread_ts: str
    tags: str


def create_question(question: QuestionCreate):
    with engine.connect() as conn:
        conn.execute(questions_table.insert().values(
            **question
        ))
        conn.commit()
        return get_question_by_thread_ts(question["thread_ts"])


RELEVANCE_THRESHOLD = 0.5


def map_question_with_relevance(q): return {
    "id": q[0],
    "channel_id": q[1],
    "thread_ts": q[2],
    "question": q[3],
    "user_id": q[4],
    "dm_id": q[5],
    "tags": q[6],
    "created_at": q[7],
    "relevance": q[8] if len(q) > 8 else None
}


def get_question_by_id(id: int):
    with engine.connect() as conn:
        result = conn.execute(questions_table.select().where(
            questions_table.c.id == id)).fetchone()
        return dict(map_question_with_relevance(result))


def get_question_by_thread_ts(thread_ts: str):
    with engine.connect() as conn:
        result = conn.execute(questions_table.select().where(
            questions_table.c.thread_ts == thread_ts)).fetchone()
        return dict(map_question_with_relevance(result))


def get_question_by_tags(tags: str, limit: int = 5):
    sql = text("""
               SELECT *, MATCH(tags) AGAINST(:tags IN BOOLEAN MODE) as relevance
               FROM questions
               WHERE MATCH(tags) AGAINST(:tags IN BOOLEAN MODE)
               ORDER BY relevance DESC
               LIMIT :limit
               """)
    with engine.connect() as conn:
        result = conn.execute(sql, {"tags": tags, "limit": limit})
        return list(map(map_question_with_relevance, result.fetchall()))


def get_question_by_question(question: str, limit: int = 5):
    sql = text("""
               SELECT *, MATCH(question) AGAINST(:question IN NATURAL LANGUAGE MODE) as relevance
               FROM questions
               WHERE MATCH(question) AGAINST(:question IN NATURAL LANGUAGE MODE) > :threshold
               ORDER BY relevance DESC
               LIMIT :limit
               """)
    with engine.connect() as conn:
        result = conn.execute(
            sql, {"question": question, "limit": limit, "threshold": RELEVANCE_THRESHOLD})
        return list(map(map_question_with_relevance, result.fetchall()))
