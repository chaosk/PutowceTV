from os import path
import shlex
import subprocess
import logging
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

_ps = []

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


def make_process_cache():
	_ps = []
	for proc in psutil.process_iter():
		try:
			_ps.append(proc.as_dict(attrs=['pid', 'cmdline']))
		except psutil.NoSuchProcess:
			pass


def running(child):
	if 'pidfile' in child:
		return path.isfile(child['pidfile'])
	else:
		try:
			(p['cmdline'] for p in _ps if p['cmdline'] == child['start']).next()
		except StopIteration:
			return False
		else:
			return True


def start(child):
	logger.info("Starting {}...".format(child['name']))
	if running(child):
		logger.warning("{} is already running.".format(child['name']))
		return
	devnull = open('/dev/null', 'w')
	subprocess.Popen(
		shlex.split(child['start']),
		close_fds=True,
		cwd=child.get('cwd', None),
		stdout=devnull,
		stderr=devnull
	)


def stop(child):
	logger.info("Stopping {}...".format(child['name']))
	if not running(child):
		logger.warning("{} is already not running".format(child['name']))
		return
	if 'stop' in child:
		devnull = open('/dev/null', 'w')
		subprocess.Popen(
			shlex.split(child['stop']),
			close_fds=True,
			cwd=child.get('cwd', None),
	                stdout=devnull,
			stderr=devnull
		)
	else:
		try:
			p = (p['cmdline'] for p in _ps if p['cmdline'] == child['start']).next()
		except:
			pass
		else:
			psutil.Process(p['pid']).kill()


def start_all():
	for child in meta:
		start(child)


def stop_all():
	for child in meta:
		stop(child)


action_map = {
	'start': start_all,
	'stop': stop_all,
}


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description="putowcetv")
	parser.add_argument("action", type=str, choices=("start", "stop"),
		help="whether to 'start' or 'stop' PutowceTV.")
	args = parser.parse_args()

	make_process_cache()
	action_map[args.action]()
