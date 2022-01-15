import csv
import datetime

import pandas as pd
from flask import Flask
from flask_pydantic import validate
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from config import POSSIBLE_TYPES, POSSIBLE_GROUPINGS, EXCLUDED_ATTRS, GROUPING_VALUES
from models import EventModel

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)


class Event(db.Model):
    id = db.Column(db.String, primary_key=True, index=True)
    asin = db.Column(db.String)
    brand = db.Column(db.String)
    source = db.Column(db.String)
    stars = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Id {self.id}>"


def append_to_response(
        response: list,
        key: str,
        val: int,
        days: int,
        data_type: str = "usual",
        cumulative_value: int = 0
) -> int:
    """
    Forms dict with received args and append it to response array.
    If data_type==cumulative, returns new value of this variable, and 0, if data_type==usual.

    :param response: Simple array performed as list, containing dicts.
    :param key: Datetime in str.
    :param val: Counter as int.
    :param days: Days in timedelta as int.
    :param data_type: Affects the calculation algorithm. Possible types: "usual", "cumulative"
    :param cumulative_value: Stores intermediate value for calculation algorithm.
    :return: cumulative_value as int.
    """
    # If Type=usual, just append data to response array
    if data_type == "usual":
        response.append({"date": key, "value": val, "days": days})

    # Make changes to the calculation algorithm if Type=cumulative
    elif data_type == "cumulative":
        cumulative_value += val
        response.append({"date": key, "value": cumulative_value, "days": days})

    return cumulative_value


def count_days_between_timestamp(
        start: datetime.datetime,
        end: datetime.datetime
) -> int:
    """
    Converts timedelta to days number.

    :param start: Start of period as datetime.
    :param end: End of period as datetime.
    :return: Number of days during the time period.
    """
    delta = end - start
    return delta.days


def count_data_between_timestamp(
        start: datetime.datetime,
        end: datetime.datetime,
        filters: dict
) -> int:
    """
    Makes a query to the DB according to received args and counts items from response.

    :param filters: Dict of filters that will be applied to SQL query formation
    :param start: Start of period as datetime.
    :param end: End of period as datetime.
    :return: Number of items falling within the time period.
    """
    if any(filters.values()):
        filters = {key: value for key, value in filters.items() if value}
        queryset = db.session.query(Event)

        for attr, value in filters.items():
            if isinstance(value, list):
                queryset = queryset.filter(getattr(Event, attr).in_(value))
            else:
                queryset = queryset.filter(getattr(Event, attr) == value)

        return queryset.filter(Event.timestamp.between(start, end)).count()

    return db.session.query(Event).filter(Event.timestamp.between(start, end)).count()


def format_datetime(dt: datetime.datetime) -> str:
    """
    Simply formats datetime to str in required format.

    :param dt: Datetime object.
    :return: Formatted datetime object as str.
    """
    return dt.strftime("%Y-%m-%d")


def get_attributes() -> list:
    """
    Parses attributes from 1st row in csv file.

    :return: List of attributes.
    """
    with open("../data.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        response = [attr for attr in next(csv_reader) if attr not in EXCLUDED_ATTRS]
    return response


def get_possible_filters() -> dict:
    """
    Gets list of all unique filters for every attribute from DB.

    :return: List of dict where key=attribute name and value=list of unique filters.
    """
    response = {}
    for attr in get_attributes():
        values = [
            value[0] for value in db.session.query(getattr(Event, attr)).distinct()
        ]
        response.update({attr: values})
    return response


def form_filters(query: EventModel) -> dict:
    """
    Forms filters and it's values in beautiful dict format.

    :param query: Pydantic EventModel object.
    :return: Dict where key=attribute name and value=attribute value.
    """
    filter_attributes = get_attributes()
    filter_values = (query.asin, query.brand, query.source, query.stars)
    return dict(zip(filter_attributes, filter_values))


def get_data(
        start: datetime.datetime,
        end: datetime.datetime,
        grouping: str,
        data_type: str,
        filters: dict
) -> list:
    """
    Gets data from DB and forms it according to received arguments.

    :param filters: Dict of filters that will be applied to SQL query formation
    :param data_type: Type of result calculation.
    :param start: Period start date as datetime.datetime.
    :param end: Period end date as datetime.datetime.
    :param grouping: Grouping key as str. Affects the polling frequency step.
    :return: List of dicts that displays final result.
    """
    response = []

    frequency = GROUPING_VALUES.get(grouping)
    time_periods = (
        pd.date_range(start, end, freq=frequency).values.astype("datetime64[s]").tolist()
    )
    time_periods_length = len(time_periods)

    key = format_datetime(start)
    cumulative_value = 0

    # If timestamp less then frequency, just return counter.
    if not time_periods_length:
        value = count_data_between_timestamp(start, end, filters)
        days = count_days_between_timestamp(start, end)
        append_to_response(response, key, value, days)
        return response

    for num, val in enumerate(time_periods, 1):

        # On first iteration we're calculating timedelta between start-value from URL params and intermediate end-value
        if num == 1:
            dynamic_end = time_periods[num-1]
            value = count_data_between_timestamp(start, dynamic_end, filters)
            days = count_days_between_timestamp(start, dynamic_end)

        # Then just reassign start and end values and move along the timeline
        else:
            dynamic_start = time_periods[num-2]
            dynamic_end = time_periods[num-1]
            key = format_datetime(dynamic_start)
            value = count_data_between_timestamp(dynamic_start, dynamic_end, filters)
            days = count_days_between_timestamp(dynamic_start, dynamic_end)

        # If Type=cumulative, function will return new value of cumulative_value and we are saving it for next iteration
        cumulative_value = append_to_response(
            response=response,
            key=key,
            val=value,
            days=days,
            data_type=data_type,
            cumulative_value=cumulative_value
        )

    #  If it still some days left after last iteration, add them to result | frequency > count(days_left) != 0
    if dynamic_end < end:
        key = format_datetime(dynamic_end)
        value = count_data_between_timestamp(dynamic_end, end, filters)
        days = count_days_between_timestamp(dynamic_end, end)

        # Even if Type=cumulative, we don't care anymore about cumulative_value cuz it is last iteration
        append_to_response(
            response=response,
            key=key,
            val=value,
            days=days,
            data_type=data_type,
            cumulative_value=cumulative_value
        )

    return response


class Index(Resource):
    def get(self) -> dict:
        """
        Home page handler.

        :return: Dict with welcome message
        """
        return {
            "msg": "Hello, nice to meet you!",
            "info": "/api/info",
            "timeline": "/api/info",
        }


class Info(Resource):
    def get(self) -> dict:
        """
        Simple GET request handler.

        :return: Dict with some info about API which will be formatted to JSON
        """
        return {
            "startDate": "Start of period in format YYYY-MM-DD",
            "endDate": "End of period in format YYYY-MM-DD",
            "Type": POSSIBLE_TYPES,
            "Grouping": POSSIBLE_GROUPINGS,
            "Filters": get_possible_filters(),
        }


class Timeline(Resource):
    @validate()
    def get(self, query: EventModel) -> dict:
        """
        GET request handler with URL params parser.

        :param query: Pydantic params validator
        :return: Dict which will be formatted to JSON
        """
        filters = form_filters(query)
        data = get_data(query.startDate, query.endDate, query.Grouping, query.Type, filters)

        total_days = count_days_between_timestamp(query.startDate, query.endDate)
        return {
            "success": True,
            "quantity": len(data),
            "total days": total_days,
            "timeline": data
        }


api.add_resource(Index, "/")
api.add_resource(Info, "/api/info")
api.add_resource(Timeline, "/api/timeline")

if __name__ == "__main__":
    app.run(debug=True)
