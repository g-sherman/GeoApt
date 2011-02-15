# Makefile for GeoApt - builds the UI and resource files
# Copyright (C) 2010 Gary Sherman
# Licensed under the terms of GNU GPL 2

VERSION = 0.1.3
#
# Build UI files and resources
UISOURCES = mainwindow_ui.py resources.py dlgAddThemeFolder_ui.py dlgAddTheme_ui.py dlgAboutGeoApt_ui.py
PYSOURCES = GeoApt.py \
					geoapt_version.py \
					about_geoapt.py \
					add_theme.py \
					add_theme_folder.py \
					theme.py \
					theme_database.py \
					theme_tree.py 

EXTRAS = run.sh run.cmd README

all: $(UISOURCES)

clean:
	rm -f $(UISOURCES)
	rm -f *.pyc
	rm -f *~

%_ui.py : %.ui
	pyuic4 -o $@ $<

resources.py: resources.qrc
	pyrcc4 -o resources.py resources.qrc

dist: all
	DATE= date "+ %Y-%m-%d"
	ZIPFILE=geapt_$(VERSION)_$(DATE).zip
	rm -f geoapt_$(VERSION).zip
	rm -rf ./geoapt_$(VERSION)
	mkdir -p geoapt_$(VERSION)
	cp $(PYSOURCES) $(EXTRAS) geoapt_$(VERSION)
	cp $(UISOURCES) geoapt_$(VERSION)
	zip -9v geoapt_$(VERSION).zip geoapt_$(VERSION)/* 

app: all
	rm -rf build dist
	python setup.py py2app --includes sip,qgis,PyQt4.QtXml --no-strip
	macdeployqt-4.6 ./dist/GeoApt.app
	./finalize_app.sh

dmg:
	#cp -r data dist
	echo "Removing GeoApt_$(VERSION).dmg if it exists"
	rm -f GeoApt_$(VERSION).dmg
	hdiutil create -imagekey zlib-level=9 -srcfolder dist GeoApt_$(VERSION).dmg


