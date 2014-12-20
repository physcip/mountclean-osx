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
	'com.apple.NotesM',
	'SandboxedService',
	'com.apple.sbd',
	'DataDetectorsDyn',
	'com.apple.InputM',
	'com.apple.NotesM',
	'com.apple.iCloud',
	'com.apple.BKAgen',
	'com.apple.appsto',
	'com.apple.geod',
	'com.apple.speech',
	'SSPasteboardHelp',
	'com.apple.Charac',
	'com.apple.audio.',
	'com.apple.intern',
	'com.apple.CoreSi',
	'com.apple.hiserv',
	'mdworker32',
	# new in Yosemite
	'iCloudAccountsMi',
	'pkd',
	'secinitd',
	# Dropbox client
	'Dropbox',
	'dbfseventsd',
	# Seafile client
	'seaf-daemon',
	'ccnet',
	# Steam games
	'ipcserver',
]

if len(sys.argv) > 1 and '--wait' not in sys.argv: # running from the LogoutHook
	users = [sys.argv[1]]
	subprocess.check_call(['/bin/launchctl', 'start', 'de.uni-stuttgart.physcip.mountclean'])
	sys.exit()
else:
	users = os.listdir('/home')

if len(users) > 0 and '--wait' in sys.argv: # deferred execution from LogoutHook
	time.sleep(10)


kill_users = []
for user in users:
	try:
		ps = subprocess.check_output(['/bin/ps', '-xoucomm', '-u', user])
	except subprocess.CalledProcessError:
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
	
