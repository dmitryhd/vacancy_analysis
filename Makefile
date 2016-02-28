all: test

test:
	nosetests-3.4 --with-coverage --cover-package=vacan --cover-erase --cover-inclusive -vx tests;

clean:
	find . -name '*.pyc' -exec rm -f {} +; find . -name '*~' -exec rm -f {} +

install:
	sudo pip3 install -r requirements.txt
