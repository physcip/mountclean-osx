mountclean
==========

This is a daemon for Mac OS X which periodically checks for leftover mounts of Network Home Directories and for stale processes belonging to users which are no longer logged in. 
In a way, this resembles what [uphclean](https://support.microsoft.com/en-us/kb/837115) did for Windows 2000/XP: it makes sure that when a user logs out, the session really ends. This is necessary so that no files are still locked when the user later logs into a different client machine. It is also useful in environments where many users share a single computer and you would otherwise end up with dozens of leftover home mounts and hundreds of stale processes.

The script is run every two minutes and checks for mounts in /home. For each one, it checks whether the corresponding user has any processes running. If he only has background processes (names listed in the script) running, these are terminated and the home directory is unmounted.
So processes and mounts belonging to a user currently logged in locally or via SSH are never touched. Also, users who e.g. started screen sessions before logging out are not touched.

Home directory mountpoints
--------------------------

__Please note that mountclean only works for home directories mounted to /home.__
It does not work for the default /Network/Servers because the OS mounts the home directory of a newly-logged-in user over the previous user's.

Our home directories are set up with the following LDAP attributes.
In our experience, this configuration has further advantages over the default, including correctly supporting Fast User Switching and multiple concurrent SSH and local logins.
We are not aware of any side effects other than being unable to mount your home directory on clients running OS X 10.6.8 and earlier.

<table>
	<tr><th>Attribute</th><th>Value</th></tr>
	<tr><th>HomeDirectory</th> <td>&lt;home_dir&gt;&lt;url&gt;afp://home.company.net/home/USER&lt;/url&gt;&lt;path&gt;&lt;/path&gt;&lt;/home_dir&gt;
	</td></tr>
	<tr><th>NFSHomeDirectory</th><td>/home/USER</td></tr>
</table>

Installation
------------
You can either clone this repository and run `make install`, or download a [pre-built installer package](https://github.com/mkuron/mountclean-osx/releases). The installer package does not include the LoginHook, which does not work reliably anyway. If the downloadable installer is not up-to-date with the latest commit, you can build the installer yourself by running `make`.

Troubleshooting
---------------
Good places to look when things don't work as expected are:
- Mounted home directories: `ls /home`
- Running processes: `ps axu | grep -v '^root\|^_'`
- Log output written by mountclean: `grep mountclean /var/log/system.log` (only on OS X 10.11.6 and below)
- Output from running mountclean: `sudo mountclean.py`
