from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


def get_or_create(session, model, **kwargs):
    try:
        instance = session.scalars(
            select(model).filter_by(**kwargs)
        ).one()
    except NoResultFound:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return instance
