from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import typing
import os

engine = create_engine(os.environ.get('DATABASE_URL'), echo=True, future=True)
Session = sessionmaker(bind=engine, future=True)
current_session = scoped_session(Session)

DeclarativeBase = declarative_base()


@contextmanager
def session(**kwargs) -> typing.ContextManager[Session]:
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def create_db():
    DeclarativeBase.metadata.create_all(engine)
