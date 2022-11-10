from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Payment(Base):
    """ Blood Pressure """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    payment_id = Column(String(250), nullable=False)
    client_id = Column(String(250), nullable=False)
    campsite = Column(String(250), nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, payment_id, client_id, campsite, number_of_guests, timestamp, trace_id):
        """ Initializes a blood pressure reading """
        self.payment_id = payment_id
        self.client_id = client_id
        self.campsite = campsite
        self.number_of_guests = number_of_guests
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['payment_id'] = self.payment_id
        dict['client_id'] = self.client_id
        dict['campsite'] = self.campsite
        dict['number_of_guests'] = self.number_of_guests
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
