from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Health(Base):
    """ Processing Statistics """

    __tablename__ = "health"

    id = Column(Integer, primary_key=True)
    receiver = Column(String, nullable=False)
    storage = Column(String, nullable=False)
    processing = Column(String, nullable=False)
    audit = Column(String, nullable=False)
    last_update = Column(DateTime, nullable=False)


    def __init__(self, receiver, storage, processing, audit, last_update):
        """ Initializes a processing statistics object """
        self.receiver = receiver
        self.storage = storage
        self.processing = processing
        self.audit = audit
        self.last_update = last_update


    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['receiver'] = self.receiver
        dict['storage'] = self.storage
        dict['processing'] = self.processing
        dict['audit'] = self.audit
        dict['last_update'] = self.last_update.strftime("%Y-%m-%dT%H:%M:%S")

        return dict