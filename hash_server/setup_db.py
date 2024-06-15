from os import environ
import logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

# Database connection parameters
db_user = environ.get('POSTGRES_USER')
db_pass = environ.get('POSTGRES_PASSWORD')
db_host = environ.get('POSTGRES_HOST')
db_name = environ.get('POSTGRES_DB')
DB_URL = (f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')

Base = declarative_base()
engine = create_engine(DB_URL)
session_factory = sessionmaker(bind=engine)

# Use thread-local sessions
MySession = scoped_session(session_factory)

# Define the Hash model
class Hashes(Base):
    __tablename__ = 'hashes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)

# Initialize the database and table
def setup_database():
    Base.metadata.create_all(engine)
    logger.info('Database setup complete.')