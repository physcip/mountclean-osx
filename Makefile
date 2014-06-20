mountclean.pkg: mountclean.py de.uni-stuttgart.physcip.mountclean.plist postflight
	pkgbuild

install: mountclean.py
	sudo cp $^ /usr/local/bin
	sudo chown root:wheel /usr/local/bin/$<
	sudo chmod go-w /usr/local/bin/$<
	sudo defaults write com.apple.loginwindow LogoutHook /usr/local/bin/$<

uninstall:
	sudo rm -f /usr/local/bin/mountclean*
	sudo defaults delete com.apple.loginwindow LogoutHook
