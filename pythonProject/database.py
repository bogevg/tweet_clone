from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()
engine = create_engine(f"postgresql+psycopg2://postgres:1111@localhost:5432/db_twit", echo = False)
Session = sessionmaker(engine)


def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()












