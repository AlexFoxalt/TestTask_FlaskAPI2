from pydantic import BaseModel, validator

from configs.config import POSSIBLE_TYPES, POSSIBLE_GROUPINGS


class IndexResponseSchema(BaseModel):
    msg: str
    info: str
    timeline: str


class InfoResponseSchema(BaseModel):
    startDate: str
    endDate: str
    Type: dict
    Grouping: dict
    Filters: dict

    @validator("Type")
    def type_validator(cls, val):
        assert val["default"] == POSSIBLE_TYPES[1]
        assert val["choices"] == POSSIBLE_TYPES

    @validator("Grouping")
    def grouping_validator(cls, val):
        assert val["default"] == POSSIBLE_GROUPINGS[0]
        assert val["choices"] == POSSIBLE_GROUPINGS

    @validator("Filters")
    def filters_validator(cls, val):
        asin = val.get("asin")
        source = val.get("source")
        stars = val.get("stars")

        for item in asin:
            if len(item) != 10:
                raise AssertionError(f"Length of each item in 'asin' must be equal to 10\n"
                                     f"Item length: {len(item)}")
            if not item.startswith("B"):
                raise AssertionError(f"Each item in 'asin' must starts with 'B'\n"
                                     f"Item starts with: {item[0]}")

        if source != ["amazon"] or not isinstance(source, list):
            raise AssertionError(f"Source must be list with 'amazon' item\n"
                                 f"Source: {source}")

        if len(stars) != 5 or sorted(stars) != list(range(1, 6)):
            raise AssertionError(f"Number of stars must be 5 and values should be in range 1-5\n"
                                 f"Stars number: {len(stars)}\n"
                                 f"Stars: {stars}")


class TimelineResponseSchema(BaseModel):
    success: bool
    quantity: int
    total_days: int
    timeline: list

    @validator("timeline")
    def timeline_validator(cls, val):
        for item in val:
            if len(item) != 3:
                raise AssertionError(f"Length of each item in 'timeline' must be equal to 3\n"
                                     f"Item length: {len(item)}")
            if not all(
                    (item.get("date") is not None,
                     item.get("value") is not None,
                     item.get("days") is not None)
            ):
                raise AssertionError(f"Each item in timeline must contain 'date', 'value', 'days' keys\n"
                                     f"Item: {item}")
