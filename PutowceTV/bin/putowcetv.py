from os import path
import shlex
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

meta = [
	{
		'name': 'crossbar',
		'pidfile': path.join(path.join(
			path.join(PROJECT_ROOT, 'PutowceTV'), '.crossbar'), 'node.pid'),
		'start': 'crossbar start',
		'stop': 'crossbar stop',
		'cwd': path.join(PROJECT_ROOT, 'PutowceTV')
	},
	{
		'name': 'klein',
		'start': 'python -m PutowceTV.app',
		'cwd': PROJECT_ROOT,
	}
]


def running(child):
	if 'pidfile' in child:
		return path.isfile(child['pidfile'])
	else:
		ps = subprocess.Popen(shlex.split('ps cax'), stdout=subprocess.PIPE)
		output = ps.communicate()[0]
		return "{}\n".format(child['start']) in output


def start():
	for child in meta:
		logger.info("Starting {}...".format(child['name']))
		if running(child):
			logger.warning("{} is already running".format(child['name']))

		subprocess.Popen(
			shlex.split(child['start']),
			close_fds=True,
			cwd=child.get('cwd', None)
		)


def stop():
	for child in meta:
		logger.info("Stopping {}...".format(child['name']))
		if not running(child):
			logger.warning("{} is already not running".format(child['name']))
			continue
		if 'stop' in child:
			subprocess.Popen(
				shlex.split(child['stop']),
				close_fds=True,
				cwd=child.get('cwd', None)
			)
		else:
			pass
			# ps/kill magic


action_map = {
	'start': start,
	'stop': stop,
}


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description="putowcetv")
	parser.add_argument("action", type=str, choices=("start", "stop"),
		help="whether to 'start' or 'stop' PutowceTV.")
	args = parser.parse_args()

	action_map[args.action]()
