from abc import ABC, abstractmethod

from domain.user.user import User


class UserRepository(ABC):
    @abstractmethod
    def find_user_by_id(self, user_id: int) -> User:
        pass
