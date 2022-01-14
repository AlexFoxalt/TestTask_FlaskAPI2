from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime

from config import POSSIBLE_TYPES, POSSIBLE_GROUPINGS


class EventModel(BaseModel):
    startDate: str
    endDate: str
    Type: str
    Grouping: str
    asin: Optional[str] = None
    brand: Optional[str] = None
    source: Optional[str] = None
    stars: Optional[int] = None

    @validator("startDate", "endDate")
    def date_validator(cls, val):
        return datetime.strptime(val, "%Y-%m-%d")

    @validator("Type")
    def type_validator(cls, val):
        if val not in POSSIBLE_TYPES:
            raise ValueError("Invalid value of Type, visit /api/info for more information")
        return val

    @validator("Grouping")
    def grouping_validator(cls, val):
        if val not in POSSIBLE_GROUPINGS:
            raise ValueError("Invalid value of Grouping, visit /api/info for more information")
        return val

    @validator("brand")
    def brand_validator(cls, val):
        from app import db, Event

        brands = [value[0] for value in db.session.query(Event.brand).distinct()]
        if "," in val:
            val = val.split(",")
        for item in val:
            if item not in brands:
                raise AssertionError("Invalid value of brand, visit /api/info for more information. "
                                     "If you want to use multiple values, use comma separator")
        return val
