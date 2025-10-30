"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from cee_pipeline.database.models import Base


class Database:
    """Database manager for CEE pipeline"""

    def __init__(self, database_url: str = None):
        """
        Initialize database connection

        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "sqlite:///./cee_pipeline.db"
        )

        # Create engine
        self.engine = create_engine(
            self.database_url,
            echo=False,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables in the database"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session as context manager

        Usage:
            with db.get_session() as session:
                session.query(...)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_db(self) -> Generator[Session, None, None]:
        """
        Dependency for FastAPI to get database session

        Usage:
            @app.get("/")
            def endpoint(db: Session = Depends(database.get_db)):
                ...
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Global database instance
db = Database()
