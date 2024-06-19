import uuid
from typing import Optional, List
from datetime import date
from pydantic import BaseModel


class RevenueBase(BaseModel):
    subscription_plan_id: uuid.UUID


class RevenueCreate(RevenueBase):
    date: date


class RevenueUpdate(RevenueBase):
    income: Optional[int] = None


class RevenueOut(RevenueBase):
    id: uuid.UUID
    subscription_plan_id: uuid.UUID
    date: date
    income: int

    class Config:
        orm_mode = True


class RevenueCollectionOut(BaseModel):
    revenues: List[RevenueOut]


class RevenueInDB(RevenueBase):
    subscription_plan_id: uuid.UUID
    date: date
    income: int

    class Config:
        orm_mode = True
