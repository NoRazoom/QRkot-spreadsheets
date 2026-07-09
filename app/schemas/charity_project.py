from typing import Optional
from datetime import datetime

from pydantic import ConfigDict, NonNegativeInt, Field, BaseModel


MIN_NAME = 5
MIN_DESC = 10
MAX_NAME = 100


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, min_length=MIN_NAME, max_length=MAX_NAME)
    description: Optional[str] = Field(None, min_length=MIN_DESC)
    full_amount: Optional[NonNegativeInt] = None


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., min_length=MIN_NAME, max_length=MAX_NAME)
    description: str = Field(..., min_length=MIN_DESC)
    full_amount: int = Field(..., gt=0)
    model_config = ConfigDict(extra='forbid')


class CharityProjectUpdate(CharityProjectBase):
    model_config = ConfigDict(extra='forbid')


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None
    model_config = ConfigDict(
        from_attributes=True,
    )
