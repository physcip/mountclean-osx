mountclean.pkg: mountclean.py de.uni-stuttgart.physcip.mountclean.plist postflight
	pkgbuild

install: mountclean.py de.uni-stuttgart.physcip.mountclean.plist
	sudo cp mountclean.py /usr/local/bin
	sudo chown root:wheel /usr/local/bin/mountclean.py
	sudo chmod go-w /usr/local/bin/mountclean.py
	sudo defaults write com.apple.loginwindow LogoutHook /usr/local/bin/mountclean.py
	
	sudo cp de.uni-stuttgart.physcip.mountclean.plist /Library/LaunchDaemons
	sudo launchctl load /Library/LaunchDaemons/de.uni-stuttgart.physcip.mountclean.plist

uninstall:
	sudo rm /usr/local/bin/mountclean*
	sudo defaults delete com.apple.loginwindow LogoutHook
	
	sudo launchctl unload /Library/LaunchDaemons/de.uni-stuttgart.physcip.mountclean.plist
	sudo rm /Library/LaunchDaemons/de.uni-stuttgart.physcip.mountclean.plist
