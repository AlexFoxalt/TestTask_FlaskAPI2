COLUMN_NAME_INDEXES = {
    "asin": 0,
    "brand": 1,
    "id": 2,
    "source": 3,
    "stars": 4,
    "timestamp": 5,
}
GROUPING_VALUES = {"weekly": "W", "bi-weekly": "2W", "monthly": "M"}
POSSIBLE_TYPES = ["cumulative", "usual"]
POSSIBLE_GROUPINGS = ["weekly", "bi-weekly", "monthly"]
EXCLUDED_ATTRS = ["id", "timestamp"]
INVALID_VALUE_ERROR_TEXT = (
    "Invalid value, visit /api/info for more information. "
    "If you want to use multiple values, use comma separator"
)
