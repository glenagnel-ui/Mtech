from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from loguru import logger

Base = declarative_base()

class TestResult(Base):
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(255))
    persona = Column(String(255))
    question = Column(Text)
    expected_answer = Column(Text)
    chatbot_answer = Column(Text)
    verdict = Column(String(50))
    confidence_score = Column(Float)
    failure_category = Column(String(100))
    severity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class NeonDBHandler:
    def __init__(self):
        self.db_url = os.getenv("NEON_DB_URL")
        self.engine = None
        self.Session = None
        if self.db_url:
            try:
                # Replace postgresql:// with postgresql+psycopg2:// if needed to avoid driver issues
                if self.db_url.startswith("postgresql://"):
                    self.db_url = self.db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
                self.engine = create_engine(self.db_url)
                Base.metadata.create_all(self.engine)
                self.Session = sessionmaker(bind=self.engine)
                logger.info("Successfully connected to Neon DB and initialized tables.")
            except Exception as e:
                logger.error(f"Failed to initialize Neon DB connection: {e}")
                self.engine = None
        else:
            logger.warning("NEON_DB_URL is not set. Database logging is disabled.")

    def save_results(self, results_data: list[dict]):
        if not self.Session:
            return
            
        try:
            session = self.Session()
            for record in results_data:
                db_record = TestResult(
                    topic=record.get("topic", ""),
                    persona=record.get("persona", ""),
                    question=record.get("question", ""),
                    expected_answer=record.get("expected_answer", ""),
                    chatbot_answer=record.get("chatbot_answer", ""),
                    verdict=record.get("verdict", ""),
                    confidence_score=record.get("confidence_score", 0.0),
                    failure_category=record.get("failure_category", ""),
                    severity=record.get("severity", 0)
                )
                session.add(db_record)
            session.commit()
            session.close()
            logger.info("Test results saved to Neon DB.")
        except Exception as e:
            logger.error(f"Error saving results to Neon DB: {e}")
