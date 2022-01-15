import pytest
from datetime import datetime, timedelta

from app.utils import count_days_between_timestamp, count_data_between_timestamp


@pytest.mark.parametrize("start, end, expected_response", [
    (datetime.today() - timedelta(days=10), datetime.today(), 10),
    (datetime.today() - timedelta(days=1), datetime.today(), 1),
    (datetime.today() - timedelta(days=20), datetime.today(), 20),
])
def test_count_days_between_timestamp(start, end, expected_response):
    response = count_days_between_timestamp(start=start, end=end)
    assert response == expected_response
