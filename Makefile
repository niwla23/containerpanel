test:
	PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'

dev:
	systemctl start docker
	python3 manage.py runserver
