# -*- encoding: utf-8 -*-
import datetime
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy import Text, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from db import Base


ITEM_TYPES = {
	'message': u"Wiadomość",
	'image': "Obraz",
	'video': "Film",
	'website': "Strona",
}

WEEK_DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

WEEK_DAY_NAMES = {
	'mon': "pon.",
	'tue': "wt.",
	'wed': u"śr.",
	'thu': "czw.",
	'fri': "pt.",
	'sat': "sob.",
	'sun': "niedz.",
}


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
	week_days_bits = Column(Integer, default=0)

	@property
	def week_days(self):
		return [WEEK_DAYS[i] for i, c in enumerate(bin(self.week_days_bits)[2:].zfill(7)) if c == '1']

	@week_days.setter
	def week_days(self, value):
		self.week_days_bits = int(''.join(['1' if d in value else '0' for d in WEEK_DAYS]), 2)

	def get_week_day_display(self, week_day):
		return WEEK_DAY_NAMES[week_day]

	def get_type_display(self):
		return ITEM_TYPES[self.type]

	def short_name(self):
		if self.type == 'message':
			return u"&quot;{}&quot;".format(
				self.message[:40] + (self.message[40:] and '&ellip;'))
		return self.url

	def serialize(self, field_name):
		# srs?
		data = getattr(self, field_name)
		if type(data) == datetime.datetime:
			data = (data.year, data.month, data.day, data.hour, data.minute, data.second)
		elif type(data) == datetime.time:
			data = (data.hour, data.minute, data.second)
		return data

	def as_dict(self):
		return {c.name: self.serialize(c.name) for c in self.__table__.columns}

	def __repr__(self):
		return '<Item #{}>'.format(self.id)


class Queue(Base):
	__tablename__ = 'queue'
	id = Column(Integer, primary_key=True)
	name = Column(String(255), index=True, unique=True)
	display_name = Column(String(255), index=True, unique=True)
	text_only = Column(Boolean, default=False)

	items = relationship('Item', order_by='Item.position', backref='queue',
		collection_class=ordering_list('position'))

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def __repr__(self):
		return '<Queue {}>'.format(self.display_name)