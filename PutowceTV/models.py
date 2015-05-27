# -*- encoding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy import Text, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from db import Base


class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key=True)
	queue_id = Column(Integer, ForeignKey('queue.id'))
	position = Column(Integer)
	type = Column(Enum('message', 'image', 'video', 'website'))
	message = Column(Text)
	url = Column(String(255))
	display_time = Column(Integer, nullable=True)
	valid_since = Column(DateTime, nullable=True)
	valid_until = Column(DateTime, nullable=True)
	display_after = Column(Time, nullable=True)
	display_before = Column(Time, nullable=True)

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def __repr__(self):
		return '<Item #{}>'.format(self.id)


class Queue(Base):
	__tablename__ = 'queue'
	id = Column(Integer, primary_key=True)
	name = Column(String(255), index=True, unique=True)
	display_name = Column(String(255), index=True, unique=True)
	text_only = Column(Boolean, default=False)

	items = relationship('Item', order_by='Item.position', backref='queue',
		collection_class=ordering_list('position', count_from=1))

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def __repr__(self):
		return '<Queue {}>'.format(self.display_name)