#!/usr/bin/python

import subprocess
import sys
import os
import time
import syslog

syslog.openlog(ident=os.path.basename(sys.argv[0]), facility=syslog.LOG_AUTH)
def log(msg):
	print msg
	syslog.syslog(str(msg))

killprocs = [
	# Processes left over after an SSH session
	'launchd',
	'distnoted', 
	'cfprefsd',
	'xpcd',
	'tccd',
	'com.apple.IconSe',
	'secd',
	'IMDPersistenceAg',
	'CloudKeychainPro',
	'NetAuthSysAgent',
	'gssd',
	'mdworker',
	# More processes left over after a GUI login
	'mdflagwriter',
	'syncdefaultsd',
	'lsregister',
	'CVMCompiler',
	'com.apple.ShareK',
	'Dropbox',
	'dbfseventsd',
]

if len(sys.argv) > 1: # running from the LogoutHook
	users = [sys.argv[1]]
else:
	users = os.listdir('/home')

kill_users = []
for user in users:
	try:
		ps = subprocess.check_output(['/bin/ps', '-xoucomm', '-u', user])
	except CalledProcessError:
		log("No running processes for %s" % user)
		kill_users.append(user)
		continue
	ps = ps.splitlines()
	ps = [p.strip() for p in ps[1:]]
	extraps = set(ps)-set(killprocs)
	log("%d processes still running: %s" % (len(extraps), ", ".join(extraps)))
	
	if len(extraps) == 0:
		kill_users.append(user)
		log("Killing processes for %s" % user)
		subprocess.call(['/usr/bin/killall', '-u', user])

if len(kill_users) > 0:
	time.sleep(2)
	for user in kill_users:
		log("Killing leftover processes for %s" % user)
		subprocess.call(['/usr/bin/killall', '-9', '-u', user])
		homedir = '/home/' + user
		if os.path.exists(homedir):
			log("Unmounting homedir for %s" % user)
			subprocess.call(['/sbin/umount', '-f', homedir])
	
