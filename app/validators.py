from typing import Optional, Union
from pydantic import BaseModel, validator
from datetime import datetime

from configs.config import POSSIBLE_TYPES, POSSIBLE_GROUPINGS, INVALID_VALUE_ERROR_TEXT
from models import db, Event


def get_values(attr: str) -> list:
    """
    Parses all unique column values according to attr.

    :param attr: Name of column as str.
    :return: List of unique values.
    """
    return [value[0] for value in db.session.query(getattr(Event, attr)).distinct()]


class EventModel(BaseModel):
    startDate: str
    endDate: str
    Type: str = "usual"
    Grouping: str = "weekly"
    asin: Optional[str] = None
    brand: Optional[str] = None
    source: Optional[str] = None
    stars: Optional[Union[int, str]] = None

    @validator("startDate")
    def start_date_validator(cls, val):
        return datetime.strptime(val, "%Y-%m-%d")

    @validator("endDate")
    def end_date_validator(cls, val, values):
        startDate = values.get("startDate")
        if not startDate:
            raise ValueError(
                "startDate not provided"
            )
        endDate = datetime.strptime(val, "%Y-%m-%d")
        if startDate > endDate:
            raise ValueError(
                "endDate cannot be less then startDate"
            )
        return endDate

    @validator("Type")
    def type_validator(cls, val):
        if val not in POSSIBLE_TYPES:
            raise ValueError(
                "Invalid value of Type, visit /api/info for more information"
            )
        return val

    @validator("Grouping")
    def grouping_validator(cls, val):
        if val not in POSSIBLE_GROUPINGS:
            raise ValueError(
                "Invalid value of Grouping, visit /api/info for more information"
            )
        return val

    # Filters

    @validator("asin")
    def asin_validator(cls, val):
        asins = get_values("asin")

        # Multiple values case with comma separator
        if "," in val:
            val = val.split(",")
            for item in val:
                if item not in asins:
                    raise ValueError(INVALID_VALUE_ERROR_TEXT)

        # Single value case
        else:
            if val not in asins:
                raise ValueError(INVALID_VALUE_ERROR_TEXT)

        return val

    @validator("brand")
    def brand_validator(cls, val):
        brands = get_values("brand")

        if "," in val:
            val = val.split(",")
            for item in val:
                if item not in brands:
                    raise ValueError(INVALID_VALUE_ERROR_TEXT)
        else:
            if val not in brands:
                raise ValueError(INVALID_VALUE_ERROR_TEXT)

        return val

    @validator("source")
    def source_validator(cls, val):
        sources = get_values("source")

        if "," in val:
            val = val.split(",")
            for item in val:
                if item not in sources:
                    raise ValueError(INVALID_VALUE_ERROR_TEXT)
        else:
            if val not in sources:
                raise ValueError(INVALID_VALUE_ERROR_TEXT)

        return val

    @validator("stars")
    def stars_validator(cls, val):
        stars = get_values("stars")

        if isinstance(val, str):
            if "," in val:
                val = [int(v) for v in val.split(",")]
                for item in val:
                    if item not in stars:
                        raise ValueError(INVALID_VALUE_ERROR_TEXT)
            else:
                raise ValueError(INVALID_VALUE_ERROR_TEXT)
        else:
            if val not in stars:
                raise ValueError(INVALID_VALUE_ERROR_TEXT)
        return val
