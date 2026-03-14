from dataclasses import dataclass
from typing import Self

import bcrypt


@dataclass
class CreatePasswordService:
    @classmethod
    def build(cls) -> Self:
        return cls()

    def execute(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
