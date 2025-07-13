"""
Base service class for common service functionality
Provides common patterns for service classes
"""

from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.core.logging import get_logger

T = TypeVar('T')
logger = get_logger(__name__)


class BaseService(Generic[T]):
    """
    Base service class with common CRUD operations
    """
    
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
        self.logger = logger
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
    
    def get_by_id_or_404(self, id: int) -> T:
        """Get entity by ID or raise 404"""
        entity = self.get_by_id(id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        return entity
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except Exception as e:
            self.logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
    
    def create(self, **kwargs) -> T:
        """Create new entity"""
        try:
            entity = self.model(**kwargs)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            self.logger.info(f"Created {self.model.__name__} with ID {entity.id}")
            return entity
        except IntegrityError as e:
            self.db.rollback()
            self.logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error"
            )
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
    
    def update(self, entity: T, **kwargs) -> T:
        """Update existing entity"""
        try:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            self.db.commit()
            self.db.refresh(entity)
            self.logger.info(f"Updated {self.model.__name__} with ID {entity.id}")
            return entity
        except IntegrityError as e:
            self.db.rollback()
            self.logger.error(f"Integrity error updating {self.model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error"
            )
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating {self.model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
    
    def delete(self, entity: T) -> bool:
        """Delete entity"""
        try:
            self.db.delete(entity)
            self.db.commit()
            self.logger.info(f"Deleted {self.model.__name__} with ID {entity.id}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
    
    def count(self) -> int:
        """Count total entities"""
        try:
            return self.db.query(self.model).count()
        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
