backend-dev:
	sudo systemctl start docker
	cd backend && sudo venv/bin/python manage.py runserver

backend-migrate:
	cd backend && venv/bin/python3 manage.py makemigrations
	cd backend && sudo venv/bin/python3 manage.py migrate

frontend-dev:
	cd frontend && yarn dev

proxy-dev:
	cd proxy && sudo caddy run Caddyfile

backend-test:
	sudo systemctl start docker
	cd backend && sudo venv/bin/python3 manage.py test -v 2

frontend-test:
	cd frontend && yarn test

test:
	make backend-test
	make frontend-test

setup:
	cd backend && python3 -m venv venv
	cd backend && venv/bin/pip3 install -r requirements.txt
	cd frontend && yarn
