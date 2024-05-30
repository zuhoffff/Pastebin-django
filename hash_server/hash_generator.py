import base64
import threading
import time
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.orm import sessionmaker, declarative_base
from os import environ
from sqlalchemy.exc import OperationalError


HASH_POOL = 10
CHECK_PERIOD = 1

Base = declarative_base()

# Define the Hash table model
class Hash(Base):
    __tablename__ = 'hashes'

    id = Column(Integer, primary_key=True)
    hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)

def create_database_if_not_exists(engine, database_name):
    try:
        # Connect to the default database to create a new one
        engine.execute(text(f"CREATE DATABASE {database_name}"))
        print(f"Database '{database_name}' created successfully.")
    except OperationalError as e:
        if "already exists" in str(e):
            print(f"Database '{database_name}' already exists.")
        else:
            raise

# Create an engine that connects to the default database
default_engine = create_engine("postgresql://postgres:password@hash-db:5432/postgres")

# Create the `hashes` database if it does not exist
create_database_if_not_exists(default_engine, "hashes")

# Create a database engine and session
engine = create_engine(environ.get('POSTGRES_URL'))
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
            session.add(new_hash)
        time.sleep(CHECK_PERIOD)

def get_next_unused_hash():
    next_hash = session.query(Hash).filter_by(used=False).order_by(Hash.id).first()
    if next_hash:
        next_hash.used = True
        session.commit()
        return next_hash.hash
    return None

def hash_generator_thread():
    threading.Thread(target=ensure_spare_hashes, daemon=True).start()

def main():
    initialize_table()
    hash_generator_thread()

if __name__ == '__main__':
    main()
    print(get_next_unused_hash())
