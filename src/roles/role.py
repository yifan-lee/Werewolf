
from abc import ABC, abstractmethod
from src.config import RoleType

class Role(ABC):
    def __init__(self, role_type: RoleType):
        self.role_type = role_type

    @property
    def name(self):
        return self.role_type.value

    def __str__(self):
        return self.name
