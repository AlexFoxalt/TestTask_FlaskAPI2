import csv
from datetime import datetime

from models import db, Event
from configs.config import COLUMN_NAME_INDEXES


def fill_db() -> None:
    """
    Just moves data from .csv file to DB.
    :return: None
    """
    with open("../data.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        # Skip the row with column names
        next(csv_reader)

        identifier = COLUMN_NAME_INDEXES.get("id")
        asin = COLUMN_NAME_INDEXES.get("asin")
        brand = COLUMN_NAME_INDEXES.get("brand")
        source = COLUMN_NAME_INDEXES.get("source")
        stars = COLUMN_NAME_INDEXES.get("stars")
        timestamp = COLUMN_NAME_INDEXES.get("timestamp")

        for row in csv_reader:
            db.session.add(
                Event(
                    id=row[identifier],
                    asin=row[asin],
                    brand=row[brand],
                    source=row[source],
                    stars=row[stars],
                    timestamp=datetime.fromtimestamp(int(row[timestamp])),
                )
            )

        db.session.commit()
        print("DB filled successfully!")


if __name__ == "__main__":
    fill_db()
