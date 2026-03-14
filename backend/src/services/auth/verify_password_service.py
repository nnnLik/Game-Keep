from dataclasses import dataclass
from typing import Self

import bcrypt


@dataclass
class VerifyPasswordService:
    @classmethod
    def build(cls) -> Self:
        return cls()

    def execute(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
