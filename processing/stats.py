from sqlalchemy import Column, Integer, String, DateTime
from base import Base

class Stats(Base):

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_book = Column(Integer, nullable=False)
    num_payment = Column(Integer, nullable=False)
    sum_book_total = Column(Integer, nullable=False)
    avg_book_total = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)
    

    def __init__(self, num_book, num_payment, sum_book_total, avg_book_total, last_updated):
        self.num_book = num_book
        self.num_payment = num_payment
        self.sum_book_total = sum_book_total
        self.avg_book_total = avg_book_total
        self.last_updated = last_updated

    def to_dict(self):
        dict = {}
        dict['num_book'] = self.num_book
        dict['num_payment'] = self.num_payment
        dict['sum_book_total'] = self.sum_book_total
        dict['avg_book_total'] = self.avg_book_total
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")

        return dict