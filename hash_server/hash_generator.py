import base64
import threading
import time
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.orm import sessionmaker, declarative_base
from os import environ
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import database_exists, create_database
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

db_user = environ.get('POSTGRES_USER')
db_pass = environ.get('POSTGRES_PASSWORD')
db_host = environ.get('POSTGRES_HOST')
db_name = environ.get('POSTGRES_DB')

HASH_POOL = 10
CHECK_PERIOD = 1

Base = declarative_base()

# Define the Hash table model
class Hash(Base):
    __tablename__ = db_name

    id = Column(Integer, primary_key=True)
    hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)
    
# Create db engine
# Create the `hashes` database if it does not exist
engine = create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')
if not database_exists(engine.url): create_database(engine.url)

# Create a database session
Session = sessionmaker(bind=engine)
session = Session()

def initialize_table():
    Base.metadata.create_all(engine)

def generate_hash(id):
    return base64.b64encode(str(id).encode()).decode()

def count_unused_hashes():
    return session.query(Hash).filter_by(used=False).count()

def ensure_spare_hashes():
    while True:
        unused_count = count_unused_hashes()
        if unused_count < HASH_POOL:
            new_hash_id = session.query(Hash).count() + 1
            new_hash = Hash(id=new_hash_id, hash=generate_hash(new_hash_id))

            LOGGER.info(new_hash)
            
            session.add(new_hash)
            session.commit()
        time.sleep(CHECK_PERIOD)

def get_next_unused_hash():
    next_hash = session.query(Hash).filter_by(used=False).first()
    LOGGER.info(next_hash)
    if next_hash:
        next_hash.used = True
        session.commit()
        return next_hash.hash
    return None

def main():
    initialize_table()
    ensure_spare_hashes()

# For debugging: 
if __name__ == '__main__':
    main()
    print(get_next_unused_hash())



# def generate_hash(seed):
#     seed_bytes = str(seed).encode("ascii") 
#     base64_bytes = base64.b64encode(seed_bytes) 
#     base64_string = base64_bytes.decode("ascii") 
#     return base64_string

# def decode_hash(hash):
#     base64_bytes = str(hash).encode("ascii")
#     base64_bytes = base64.b64decode(base64_bytes) 
#     original_seed = base64_bytes.decode('ascii')
#     return original_seed
