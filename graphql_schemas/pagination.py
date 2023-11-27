from typing import Generic, List, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.type
class LimitOffsetPage(Generic[T]):
    limit: int
    offset: int
    count: int
    items: List[T]
