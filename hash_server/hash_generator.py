import base64
import logging
from os import environ
from sqlalchemy import create_engine, Column, Integer, String, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
db_user = environ.get('POSTGRES_USER')
db_pass = environ.get('POSTGRES_PASSWORD')
db_host = environ.get('POSTGRES_HOST')
db_name = environ.get('POSTGRES_DB')
DB_URL = (f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')

# Specify configuration constants 
HASH_POOL = 100
CHECK_PERIOD = 1

# SQLAlchemy setup
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Hash model
class Hash(Base):
    __tablename__ = 'hashes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)

# Initialize the database and table
def setup_database():
    logger.info('Setting up the database.')
    Base.metadata.create_all(engine)
    logger.info('Database setup complete.')

# Generate a new hash based on the id
def generate_hash(id):
    return base64.b64encode(str(id).encode()).decode()

# Insert a new hash into the database
def insert_new_hash():
    with Session() as session:
        last_id = session.query(func.max(Hash.id)).scalar() or 0
        new_hash = generate_hash(last_id + 1)
        hash_entry = Hash(hash=new_hash)
        session.add(hash_entry)
        session.commit()
        logger.info(f'Inserted new hash: {new_hash}')

# Count unused hashes
def count_unused_hashes():
    with Session() as session:
        count = session.query(func.count(Hash.id)).filter_by(used=False).scalar()
        logger.info(f'Number of unused hashes: {count}')
        return count

# Ensure a certain number of spare hashes
def ensure_spare_hashes(n=100):
    logger.info(f'Ensuring at least {n} spare hashes.')
    current_unused = count_unused_hashes()
    while current_unused < n:
        insert_new_hash()
        current_unused += 1

# Get the next unused hash
def get_next_unused_hash():
    with Session() as session:
        try:
            hash_entry = session.query(Hash).filter_by(used=False).order_by(Hash.id).first()
            if hash_entry:
                hash_entry.used = True
                session.commit()
                logger.info(f'Retrieved unused hash: {hash_entry.hash}')
                return hash_entry.hash
            # Ran out of hashes due to high activity, restore them:
            insert_new_hash()   
            hash_entry = session.query(Hash).filter_by(used=False).order_by(Hash.id).first()
            return hash_entry.hash
        
        except Exception as e:
            session.rollback()
            logger.error(f'Error retrieving unused hash: {e}')
            return None
        
# Main function for initialization
def main():
    setup_database()
    ensure_spare_hashes(HASH_POOL)  # Ensure there are at least 10 spare hashes

if __name__ == '__main__':
    main()