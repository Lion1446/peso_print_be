from flask_sqlalchemy import SQLAlchemy     ## pip3 install Flask-SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class PrintJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    datetime_deleted = db.Column(db.DateTime, nullable=True, default=None)
    is_printed = db.Column(db.Boolean, nullable=False, default=False)
    queue_code = db.Column(db.String(20), nullable=False)
    absolute_file_path = db.Column(db.String(100))
    amount_payable = db.Column(db.Float, nullable=False)
    copies = db.Column(db.Integer, nullable=False)
    is_colored = db.Column(db.Boolean, nullable=False)
    pages_to_print = db.Column(db.Text, nullable=False)
    paper_size = db.Column(db.String(20), nullable=False)

    def to_map(self):
        string_datetime_created = self.datetime_created.strftime("%Y-%m-%d %H:%M:%S")
        if self.datetime_deleted is not None:
            string_datetime_deleted = self.datetime_deleted.strftime("%Y-%m-%d %H:%M:%S")
        else:
            string_datetime_deleted = None
        return {
            "id": self.id,
            "datetime_created": string_datetime_created,
            "datetime_deleted": string_datetime_deleted,
            "is_printed": self.is_printed,
            "queue_code": self.queue_code,
            "absolute_file_path": self.absolute_file_path,
            "amount_payable": self.amount_payable,
            "copies": self.copies,
            "is_colored": self.is_colored,
            "pages_to_print": self.pages_to_print,
            "paper_size": self.paper_size
        }
    
