#!/usr/bin/env python
# Makefile for Geonibble - builds the UI and resource files
# Copyright (C) 2009 Gary Sherman
# Licensed under the terms of GNU GPL 2

all: mainwindow_ui.py resources.py

clean:
	rm -f mainwindow_ui.py resources.py
	rm -f *.pyc
	rm -f *~

mainwindow_ui.py: mainwindow.ui
	pyuic4 -o mainwindow_ui.py mainwindow.ui
	
resources.py: resources.qrc
	pyrcc4 -o resources.py resources.qrc

