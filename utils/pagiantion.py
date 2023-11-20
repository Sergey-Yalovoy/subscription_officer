from pydantic import BaseModel


class PaginationSchema(BaseModel):
    limit: int
    offset: int
    count: int
