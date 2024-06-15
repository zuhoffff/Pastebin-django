import logging
from sqlalchemy import func
import base64
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class AbstractHashDbWizard(ABC):
    @abstractmethod
    def __init__(self, Session, db_model) -> None:
        self.Session = Session
        self.db_model = db_model
    
    # Generate a new hash based on the id
    @staticmethod
    @abstractmethod
    def generate_hash(id):
        pass
        
    @abstractmethod
    def insert_new_hashes(self, amount):
        pass

    # Count unused hashes
    def count_unused_hashes(self):
        pass
        
    # Get the next unused hash
    def get_next_unused_hash(self):
        pass

class HashDbWizard(AbstractHashDbWizard):
    
    def __init__(self, engine, db_model) -> None:
        super().__init__(engine, db_model)

    @staticmethod
    def generate_hash(id):
        return base64.b64encode(str(id).encode()).decode()
  
    def insert_new_hashes(self, amount) -> None:
        with self.Session() as session:
            for i in range(amount):
                last_id = session.query(func.max(self.db_model.id)).scalar() or 0
                curr_id = last_id+1
                new_hash = self.generate_hash(curr_id)
                hash_entry = self.db_model(hash=new_hash)
                session.add(hash_entry)
                session.commit()
                session.close()

    # Count unused hashes
    def count_unused_hashes(self):
        with self.Session() as session:
            count = session.query(func.count(self.db_model.id)).filter_by(used=False).scalar()
            session.close()
            return count
        
    # Get the next unused hash
    def get_next_unused_hash(self):
        with self.Session() as session:
            next_hash_entry = session.query(self.db_model).filter_by(used=False).first() 
            next_hash_entry.used = True
            session.commit()
            session.close()
            return next_hash_entry.hash