# Makefile for GeoApt - builds the UI and resource files
# Copyright (C) 2010 Gary Sherman
# Licensed under the terms of GNU GPL 2


#
# Build UI files and resources
UISOURCES = mainwindow_ui.py resources.py dlgAddThemeFolder_ui.py dlgAddTheme_ui.py

all: $(UISOURCES)

clean:
	rm -f $(UISOURCES)
	rm -f *.pyc
	rm -f *~

%_ui.py : %.ui
	pyuic4 -o $@ $<

resources.py: resources.qrc
	pyrcc4 -o resources.py resources.qrc

