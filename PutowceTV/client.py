# -*- encoding: utf-8 -*-
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class Component(ApplicationSession):

	@inlineCallbacks
	def onJoin(self, details):
		print("session attached")
		queues = yield self.call('tv.putowce.retrieve')
		print("Queues:", queues)
		sub = yield self.subscribe(self.on_event, 'tv.putowce.update')
		print("Subscribed to 'tv.putowce.update' with {}".format(sub.id))

	def on_event(self, i):
		print("Got an update: {}".format(i))

	def onDisconnect(self):
		print("disconnected")
		if reactor.running:
			reactor.stop()


if __name__ == '__main__':
	runner = ApplicationRunner("ws://localhost:8080/ws", "realm1", debug=True)
	runner.run(Component)