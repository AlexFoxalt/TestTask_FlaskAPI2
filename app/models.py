from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Event(db.Model):
    id = db.Column(db.String, primary_key=True, index=True)
    asin = db.Column(db.String)
    brand = db.Column(db.String)
    source = db.Column(db.String)
    stars = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Id {self.id}>"
