from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import typing
import os

engine = create_engine(os.environ.get('DATABASE_URL'), echo=True)
Session = sessionmaker(bind=engine)
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


def get_or_create(model, **kwargs):
    with session() as s:
        instance = s.query(model).filter_by(**kwargs).one_or_none()
        if instance is None:
            instance = model(**kwargs)
            try:
                s.add(instance)
                s.commit()
            except Exception:
                s.rollback()
                raise

    return instance


def create_db():
    DeclarativeBase.metadata.create_all(engine)
