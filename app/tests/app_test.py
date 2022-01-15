import pytest
import requests

from app.tests.configs.config import URL, OK, BAD_REQUEST, NOT_FOUND
from tests.schemas.schemas import IndexResponseSchema, InfoResponseSchema, TimelineResponseSchema


@pytest.mark.parametrize("rout, expected_status", [
    ('', OK),

    ("api/info", OK),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02", OK),
    ("api/timeline?startDate=2010-01-01&endDate=2011-01-01", OK),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Type=cumulative", OK),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Type=usual", OK),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=weekly", OK),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=bi-weekly", OK),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=monthly", OK),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&brand=Downy", OK),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&brand=Downy,Snuggle", OK),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&source=amazon", OK),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&source=amazon,amazon", OK),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&stars=1", OK),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&stars=1,2,3,4", OK),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&asin=B0014D3N0Q", OK),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&asin=B07SXC6VDM,B00463EPKI", OK),
])
def test_positive_status(rout, expected_status):
    r = requests.get(URL + rout)
    assert r.status_code == expected_status


@pytest.mark.parametrize("rout, expected_status", [
    ('123', NOT_FOUND),
    ("api/inf", NOT_FOUND),
    # No params
    ("api/timeline", BAD_REQUEST),
    # No required params: start/end dates
    ("api/timeline?startDate=2010-01-01", BAD_REQUEST),
    ("api/timeline?endDate=2019-01-02", BAD_REQUEST),
    # startDate > endDate
    ("api/timeline?startDate=2020-01-01&endDate=2010-01-02", BAD_REQUEST),
    # Invalid Type
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Type=comulative", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Type=USUAL", BAD_REQUEST),
    # Invalid Grouping
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=WEEKLY", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=biweekly", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=weekly,monthly", BAD_REQUEST),
    # Invalid brand
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&brand=D", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&brand=Downy.Snuggle", BAD_REQUEST),
    # Invalid source
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&source=AMzon", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&source=amazon?amazon", BAD_REQUEST),
    # Invalid stars
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&stars=6", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&stars=1.2,3,4", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&stars=one", BAD_REQUEST),
    # Invalid asin
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&asin=HELLOGUYS", BAD_REQUEST),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&asin=B07SXC6VDM B00463EPKI", BAD_REQUEST),
])
def test_negative_status(rout, expected_status):
    r = requests.get(URL + rout)
    assert r.status_code == expected_status


@pytest.mark.parametrize("rout, schema", [
    ("", IndexResponseSchema),
    ("/api/info", InfoResponseSchema),

    ("api/timeline?startDate=2019-01-01&endDate=2019-03-01", TimelineResponseSchema),
    ("api/timeline?startDate=2010-01-01&endDate=2011-01-01", TimelineResponseSchema),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Type=cumulative", TimelineResponseSchema),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Type=usual", TimelineResponseSchema),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=weekly", TimelineResponseSchema),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=bi-weekly", TimelineResponseSchema),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&Grouping=monthly", TimelineResponseSchema),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&brand=Downy", TimelineResponseSchema),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&brand=Downy,Snuggle", TimelineResponseSchema),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&source=amazon", TimelineResponseSchema),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&source=amazon,amazon", TimelineResponseSchema),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&stars=1", TimelineResponseSchema),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&stars=1,2,3,4", TimelineResponseSchema),

    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&asin=B0014D3N0Q", TimelineResponseSchema),
    ("api/timeline?startDate=2019-01-01&endDate=2019-01-02&asin=B07SXC6VDM,B00463EPKI", TimelineResponseSchema)
])
def test_response_content(rout, schema):
    r_json = requests.get(URL + rout).json()
    schema.parse_obj(r_json)
