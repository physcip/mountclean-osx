VER=$(shell test -d .git && git rev-list --count HEAD || echo 0)
IDENTIFIER=de.uni-stuttgart.physcip.mountclean
SCRIPTNAME=mountclean.py

mountclean-$(VER).dmg: mountclean.pkg
	rm -f $@
	hdiutil create -srcfolder $< $@

mountclean.pkg: $(SCRIPTNAME) $(IDENTIFIER).plist postinstall preinstall
	rm -rf pkgroot pkgscripts
	mkdir pkgroot pkgscripts

	cp postinstall preinstall pkgscripts/
	mkdir -p pkgroot/{Library/LaunchDaemons,usr/local/bin}
	cp $(SCRIPTNAME) pkgroot/usr/local/bin
	cp $(IDENTIFIER).plist pkgroot/Library/LaunchDaemons
	xattr -cr pkgroot pkgscripts

	pkgbuild --version $(VER) --scripts pkgscripts --root pkgroot --identifier $(IDENTIFIER) $@

install: $(SCRIPTNAME) $(IDENTIFIER).plist
	sudo cp $(SCRIPTNAME) /usr/local/bin
	sudo chown root:wheel /usr/local/bin/$(SCRIPTNAME)
	sudo chmod go-w /usr/local/bin/$(SCRIPTNAME)
	sudo defaults write com.apple.loginwindow LogoutHook /usr/local/bin/$(SCRIPTNAME)
	
	sudo cp $(IDENTIFIER).plist /Library/LaunchDaemons
	sudo launchctl load /Library/LaunchDaemons/$(IDENTIFIER).plist

uninstall:
	sudo rm /usr/local/bin/mountclean*
	sudo defaults delete com.apple.loginwindow LogoutHook
	
	sudo launchctl unload /Library/LaunchDaemons/$(IDENTIFIER).plist
	sudo rm /Library/LaunchDaemons/$(IDENTIFIER).plist

clean:
	rm -rf *.pkg *.dmg pkgroot pkgscripts
