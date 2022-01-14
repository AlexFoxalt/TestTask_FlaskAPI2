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
        return f'<Id {self.id}>'


def append_to_response(
        response: list,
        key: str,
        val: int,
        days: int
) -> None:
    """
    Forms dict with received args and append it to response array.

    :param response: Simple array performed as list, containing dicts.
    :param key: Datetime in str.
    :param val: Counter as int.
    :param days: Days in timedelta as int.
    :return: None
    """
    return response.append({key: val, "days": days})


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
        end: datetime.datetime
) -> int:
    """
    Makes a query to the DB according to received args and counts items from response.

    :param start: Start of period as datetime.
    :param end: End of period as datetime.
    :return: Number of items falling within the time period.
    """
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
    with open('../data.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        response = [attr for attr in next(csv_reader) if attr not in EXCLUDED_ATTRS]
    return response


def get_possible_filters() -> dict:
    """
    Gets list of all unique filters for every attribute from DB.

    :return: List of dict where key=attribute name and value=list of unique filters.
    """
    response = {}
    for attr in get_attributes():
        values = [value[0] for value in db.session.query(getattr(Event, attr)).distinct()]
        response.update({attr: values})
    return response


def get_data(
        start: datetime.datetime,
        end: datetime.datetime,
        grouping: str
) -> list:
    """
    Gets data from DB and forms it according to received arguments.

    :param start: Period start date as datetime.datetime.
    :param end: Period end date as datetime.datetime.
    :param grouping: Grouping key as str. Affects the polling frequency step.
    :return: List of dicts that displays final result.
    """
    response = []

    frequency = GROUPING_VALUES.get(grouping)
    time_periods = pd.date_range(start, end, freq=frequency).values.astype('datetime64[s]').tolist()
    time_periods_length = len(time_periods)

    key = format_datetime(start)

    # If timestamp less then frequency, just return counter.
    if not time_periods_length:
        value = count_data_between_timestamp(start, end)
        days = count_days_between_timestamp(start, end)
        append_to_response(response, key, value, days)
        return response

    for num, val in enumerate(time_periods, 1):

        # On first iteration we're calculating timedelta between start-value from URL params and intermediate end-value
        if num == 1:
            dynamic_end = time_periods[num - 1]
            value = count_data_between_timestamp(start, dynamic_end)
            days = count_days_between_timestamp(start, dynamic_end)

        # Then just reassign start and end values and move along the timeline
        else:
            dynamic_start = time_periods[num - 2]
            dynamic_end = time_periods[num - 1]
            key = format_datetime(dynamic_start)
            value = count_data_between_timestamp(dynamic_start, dynamic_end)
            days = count_days_between_timestamp(dynamic_start, dynamic_end)

        append_to_response(response, key, value, days)

    #  If it still some days left after last iteration, add them to result | frequency > count(days_left) != 0
    if dynamic_end < end:
        key = format_datetime(dynamic_end)
        value = count_data_between_timestamp(dynamic_end, end)
        days = count_days_between_timestamp(dynamic_end, end)

        append_to_response(response, key, value, days)

    return response


class Info(Resource):
    def get(self):
        return {"startDate": "Start of period in format YYYY-MM-DD",
                "endDate": "End of period in format YYYY-MM-DD",
                "Type": POSSIBLE_TYPES,
                "Grouping": POSSIBLE_GROUPINGS,
                "Possible filters": get_possible_filters()
                }


class Timeline(Resource):
    @validate()
    def get(self, query: EventModel):
        data_start_date = query.startDate
        data_end_date = query.endDate
        data_type = query.Type
        grouping = query.Grouping
        brand = query.brand
        stars = query.stars

        data = get_data(data_start_date, data_end_date, grouping)
        return {'success': True,
                'quantity': len(data),
                'timeline': data}


api.add_resource(Info, '/api/info')
api.add_resource(Timeline, '/api/timeline')

if __name__ == '__main__':
    app.run(debug=True)
