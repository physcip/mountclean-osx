#!/usr/bin/python

import subprocess
import sys
import os
import time
import syslog
import pwd
import re

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
	'findNames',
	'com.apple.CloudP',
	'pluginkit',
	'ssh-agent',
	'com.apple.Speech',
	'sharingd',
	'lsuseractivityd',
	'crashpad_helper',
	'Google Chrome He',
	'LaterAgent',
	'VTDecoderXPCServ',
	'crashpad_handler',
	'diskimages-helpe',
	'com.apple.lakitu',
	'crashreporter',
	# new in El Capitan
	'com.apple.Addres',
	'GPUToolsAgent',
	'com.apple.MailSe',
	'com.apple.spotli',
	'nsurlstoraged',
	'DataclassOwnersM',
	# new in Sierra
	'trustd',
	'lsd',
	'com.apple.Dictio',
	'CalNCService',
	'languageassetd',
	'com.apple.access',
	'DiskSpaceEfficie',
	'MTLCompilerServi',
	'RdrCEF',
	'RdrCEF Helper',
	'com.apple.toneli',
	# new in High Sierra
	'com.apple.Safari',
	'ContextService',
	'com.apple.Notes.',
	'ctkd',
	'AlertNotificatio',
	# Dropbox client
	'Dropbox',
	'dbfseventsd',
	'Dropbox109',
	'DropboxMacUpdate',
	'DropboxFolderTag',
	# Seafile client
	'seaf-daemon',
	'ccnet',
	# Steam games
	'ipcserver',
]

def get_killable_users_by_mount():
	users = os.listdir('/home')
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
		log("%d processes still running for %s: %s" % (len(extraps), user, ", ".join(extraps)))
		
		if len(extraps) == 0:
			kill_users.append(user)
	return kill_users

def get_killable_users_by_launchd():
	if int(os.uname()[2].split('.')[0]) < 15:
		return []

	mounted = os.listdir('/home')

	users = []
	lines = subprocess.check_output(['/bin/launchctl', 'print', 'system'])
	for line in lines.split('\n'):
		result = re.match('\s+com.apple.xpc.launchd.domain.user.([0-9]{4,})$', line)
		if not result:
			continue
		uid = int(result.group(1))
		user = pwd.getpwuid(uid).pw_name
		homedir = pwd.getpwuid(uid).pw_dir
		log("Found user domain for %s" % user)

		if homedir.startswith('/home') and user not in mounted:
			users.append(user)

	return users

def kill(users):
	if len(users) == 0:
		return

	for user in users:
		uid = pwd.getpwnam(user).pw_uid
		if int(os.uname()[2].split('.')[0]) >= 15: # launchctl bootout was introduced by macOS 10.11
			for domain in ['gui', 'user']:
				log("Shutting down launchd " + domain + " domain")
				try:
					subprocess.call(['/bin/launchctl', 'bootout', domain + '/' + str(uid)])
				except subprocess.CalledProcessError:
					print "No " + domain + " session found"
		else:
			log("Shutting down launchd per-user bootstrap")
			subprocess.call(['/bin/launchctl', 'remove', 'com.apple.launchd.peruser.' + str(uid)])

	time.sleep(2)
	for user in users:
		log("Terminating processes for %s" % user)
		subprocess.call(['/usr/bin/killall', '-u', user])

	time.sleep(2)
	for user in users:
		log("Killing leftover processes for %s" % user)
		subprocess.call(['/usr/bin/killall', '-9', '-u', user])

	time.sleep(1)

def unmount(users):
	count = 0
	for user in users:
		homedir = '/home/' + user
		if os.path.exists(homedir):
			log("Unmounting homedir for %s" % user)
			subprocess.call(['/sbin/umount', '-f', homedir])
			count += 1

	if count > 0:
		# The LaunchServices database may contain references to apps in user home.
		# This may lead to automount storms when reading the database, like Munki does when reporting installed apps.
		log("Resetting LaunchServices database")
		subprocess.call(["/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister", "-kill", "-r", "-domain", "local", "-domain", "system", "-domain", "user"])

if __name__ == "__main__":
	users_mounted = set(get_killable_users_by_mount())
	users_launchd = set(get_killable_users_by_launchd())
	users = users_mounted.union(users_launchd)
	for arg in sys.argv[1:]:
		if not arg.startswith('-'):
			users = users.intersection(sys.argv[1:])
			users_mounted = users_mounted.intersection(sys.argv[1:])
			break
	kill(users)
	unmount(users_mounted)
