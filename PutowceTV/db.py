# -*- encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///putowce.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
										 autoflush=False,
										 bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
	import models
	Base.metadata.create_all(bind=engine)
	if db_session.query(models.Queue).count() == 0:
		db_session.add(models.Queue(name='messages',
			display_name='Belka informacyjna',
			text_only=True))
		db_session.add(models.Queue(name='main_queue',
			display_name=u'Główna kolejka'))
		db_session.commit()
