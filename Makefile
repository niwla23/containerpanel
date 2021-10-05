backend-dev:
	systemctl start docker
	cd backend && python3 manage.py runserver

backend-migrate:
	cd backend && python3 manage.py makemigrations
	cd backend && python3 manage.py migrate

frontend-dev:
	cd frontend && yarn dev

proxy-dev:
	cd proxy && caddy run Caddyfile

backend-test:
	cd backend && python3 manage.py test -v 2

frontend-test:
	cd frontend && yarn test

test:
	make backend-test
	make frontend-test

setup:
	cd backend && pip3 install -r requirements.txt
	cd frontend && yarn