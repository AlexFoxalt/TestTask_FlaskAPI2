from flask import Flask
from flask_pydantic import validate
from flask_restful import Resource, Api

from configs.config import POSSIBLE_TYPES, POSSIBLE_GROUPINGS
from models import db
from utils import (
    get_possible_filters,
    form_filters,
    get_data,
    count_days_between_timestamp,
)
from validators import EventModel


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
        data = get_data(
            query.startDate, query.endDate, query.Grouping, query.Type, filters
        )

        total_days = count_days_between_timestamp(query.startDate, query.endDate)
        return {
            "success": True,
            "quantity": len(data),
            "total_days": total_days,
            "timeline": data,
        }


# Flask setup
app = Flask(__name__)
app.config.from_pyfile("configs/dev.py")
db.init_app(app)
api = Api(app)

# API routes
api.add_resource(Index, "/")
api.add_resource(Info, "/api/info")
api.add_resource(Timeline, "/api/timeline")

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
