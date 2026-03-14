from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr

from .mixins import CreatedAtMixin


def _to_snake_case(input_str: str) -> str:
    chars = []
    for c_idx, char in enumerate[str](input_str):
        if c_idx and char.isupper():
            nxt_idx = c_idx + 1
            flag = nxt_idx >= len(input_str) or input_str[nxt_idx].isupper()
            prev_char = input_str[c_idx - 1]
            if prev_char.isupper() and flag:
                pass
            else:
                chars.append('_')
        chars.append(char.lower())
    return ''.join(chars)


class Base(AsyncAttrs, DeclarativeBase, CreatedAtMixin):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f'{_to_snake_case(cls.__name__)}'
