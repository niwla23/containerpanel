test:
	PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'

backend-dev:
	systemctl start docker
	python3 manage.py runserver

frontend-dev:
	cd frontend && yarn dev


backend-test:
	python3 manage.py test

frontend-test:
	cd frontend && yarn test

test:
	make backend-test
	make frontend-test

setup:
	pip3 install -r requirements.txt
	cd frontend && yarn