from pydantic import BaseModel


# pydantic cхема для валидации данных с POST запроса
class PostSell (BaseModel):
    product: str
    qty: int
    period: str
