from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import settings
from .logger import logger

# Database Setup
DATABASE_URL = settings.database_url or "postgresql://user:pass@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True) # usr_...
    name = Column(String)
    email = Column(String, unique=True, index=True)
    avatar = Column(String)
    provider = Column(String)
    last_login = Column(Integer)
    analyses = relationship("Analysis", back_populates="user")

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(String, primary_key=True) # analysis-...
    user_id = Column(String, ForeignKey("users.id"), index=True)
    business_idea = Column(String)
    district = Column(String)
    state = Column(String)
    date = Column(String)
    score = Column(Integer)
    recommendation = Column(String)
    project_cost = Column(Float)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")

def init_db():
    """Initializes the database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables on import for simplicity in this deployment phase
init_db()
