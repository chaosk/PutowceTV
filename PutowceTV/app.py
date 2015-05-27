# -*- encoding: utf-8 -*-
from itertools import chain
import json
from autobahn.twisted.wamp import Application
import jinja2
from klein import Klein
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import bindparam
from twisted.web.static import File
from twisted.internet.defer import inlineCallbacks, returnValue
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import NotFound
from db import db_session
from forms import ItemForm
from models import Item, Queue


wamp_app = Application('tv.putowce')


@wamp_app.register()
def retrieve():
	return [dict(chain(q.as_dict().items(),
		[['items', [i.as_dict() for i in q.items]]]))
		for q in Queue.query.outerjoin(Item).order_by(Item.position).all()]


webapp = Klein()
webapp.templates = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


@webapp.route('/')
def home(request):
	page = webapp.templates.get_template('index.html')
	return page.render(queues=db_session.query(Queue,
		func.count(Item.id)).outerjoin(Item).group_by(Queue).all())


@webapp.route('/q/<string:queue_name>')
def queue(request, queue_name):
	try:
		queue = Queue.query.outerjoin(Item).filter(
		Queue.name==queue_name).order_by(Item.position).one()
	except NoResultFound:
		raise NotFound("No matching queue has been found")
	page = webapp.templates.get_template('queue.html')
	return page.render(queue=queue)


@webapp.route('/a/<string:queue_name>', methods=['GET', 'POST'])
def add(request, queue_name):
	try:
		queue = Queue.query.filter(Queue.name==queue_name).one()
	except NoResultFound:
		raise NotFound("No matching queue has been found")
	form = ItemForm()
	if queue.text_only:
		form.type.default = 'message'
		form.type.choices = [('message', 'Message')]
	if request.method == 'POST':
		form = ItemForm(MultiDict([(k,v[0]) for k, v in request.args.items()]))
		if form.validate():
			item = Item()
			form.populate_obj(item)
			queue.items.append(item)
			db_session.commit()
			wamp_app.session.publish('tv.putowce.update', retrieve())
		request.redirect("/q/{}".format(queue.name))
		return
	page = webapp.templates.get_template('add.html')
	return page.render(form=form, queue=queue)


@webapp.route('/d/<int:item_id>', methods=['GET', 'POST'])
def delete(request, item_id):
	try:
		item = Item.query.filter(Item.id==item_id).one()
	except NoResultFound:
		raise NotFound("No matching item has been found")
	if request.method == 'POST' and request.args.get('confirm')[0]:
		queue = item.queue
		queue.items.remove(item)
		db_session.delete(item)
		db_session.commit()
		wamp_app.session.publish('tv.putowce.update', retrieve())
		request.redirect("/q/{}".format(queue.name))
		return
	page = webapp.templates.get_template('del.html')
	return page.render(item=item)


@webapp.route('/o/<string:queue_name>', methods=['POST'])
def order(request, queue_name):
	try:
		queue = Queue.query.filter(Queue.name==queue_name).one()
	except NoResultFound:
		raise NotFound("No matching queue has been found")
	stmt = Item.__table__.update().where(
		Item.id==bindparam('_id')).values(
			{'position': bindparam('position')})
	new_order = [{'_id': int(item_id), 'position': pos}
		for pos, item_id in enumerate(request.args.get('queue[]'))]
	db_session.execute(stmt, new_order)
	db_session.commit()
	wamp_app.session.publish('tv.putowce.update', retrieve())
	return json.dumps({'success': True})


@webapp.route('/static/', branch=True)
def static(request):
	return File('./static')


if __name__ == "__main__":
	import sys
	from twisted.python import log
	from twisted.web.server import Site
	from twisted.internet import reactor
	log.startLogging(sys.stdout)

	reactor.listenTCP(8000, Site(webapp.resource()))
	wamp_app.run("ws://localhost:8080/ws", "realm1")
