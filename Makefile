all: mainwindow_ui.py resources.py

clean:
	rm -f mainwindow_ui.py resources.py
	rm -f *.pyc
	rm -f *~

mainwindow_ui.py: mainwindow.ui
	pyuic4 -o mainwindow_ui.py mainwindow.ui
	
resources.py: resources.qrc
	pyrcc4 -o resources.py resources.qrc

