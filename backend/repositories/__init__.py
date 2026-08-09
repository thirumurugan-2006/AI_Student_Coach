from repositories.base import BaseRepository
from repositories.student_repository import StudentRepository, StudentCreate, StudentUpdate
from repositories.user_repository import UserRepository, UserCreate, UserUpdate

__all__ = [
    "BaseRepository",
    "StudentRepository",
    "StudentCreate",
    "StudentUpdate",
    "UserRepository",
    "UserCreate",
    "UserUpdate",
]
