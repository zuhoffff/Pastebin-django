import logging
from os import environ
from sqlalchemy import create_engine, Column, Integer, String, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
db_user = environ.get('POSTGRES_USER')
db_pass = environ.get('POSTGRES_PASSWORD')
db_host = environ.get('POSTGRES_HOST')
db_name = environ.get('POSTGRES_DB')
DB_URL = (f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')

Base = declarative_base()
engine = create_engine(DB_URL)

# Define the Hash model
class Hash(Base):
    __tablename__ = 'hashes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)

# Initialize the database and table
def setup_database():
    Base.metadata.create_all(engine)
    logger.info('Database setup complete.')

class HashDbWizard:
    
    def __init__(self, engine) -> None:
        self.Session = sessionmaker(bind=engine)
    
    # Generate a new hash based on the id
    def __generate_hash(id):
        return base64.b64encode(str(id).encode()).decode()
    
    def insert_new_hashes(self, amount) -> None:
        with self.Session() as session:
            for i in range(amount):
                last_id = session.query(func.max(Hash.id)).scalar() or 0
                new_hash = self.__generate_hash(last_id + 1)
                hash_entry = Hash(hash=new_hash)
                session.add(hash_entry)
                session.commit()
                logger.info(f'Inserted new hash: {new_hash}')

    # Count unused hashes
    def count_unused_hashes(self):
        with self.Session() as session:
            count = session.query(func.count(Hash.id)).filter_by(used=False).scalar()
            logger.info(f'Number of unused hashes: {count}')
            return count
        
    # Get the next unused hash
    def get_next_unused_hash(self):
        with self.Session() as session:
            return session.query(Hash).filter_by(used=False).first().hash