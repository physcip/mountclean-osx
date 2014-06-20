mountclean
==========

This is a daemon for Mac OS X which periodically checks for leftover mounts of Network Home Directories and for stale processes belonging to users which are no longer logged in. 
In a way, this resembles what [uphclean](http://www.microsoft.com/de-de/download/details.aspx?id=6676) did for Windows 2000/XP: it makes sure that when a user logs out, the session really ends. This is necessary so that no files are still locked when the user later logs into a different client machine. It is also useful in environments where many users share a single computer and you would otherwise end up with dozens of leftover home mounts and hundreds of stale processes.

The script is run every two minutes and checks for mounts in /home. For each one, it checks whether the corresponding user has any processes running. If he only has background processes (names listed in the script) running, these are terminated and the home directory is unmounted.
So processes and mounts belonging to a user currently logged in locally or via SSH are never touched. Also, users who e.g. started screen sessions before logging out are not touched.
