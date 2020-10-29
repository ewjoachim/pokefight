install:
	pip install -r requirements.txt

install-dev:
	pip install -r dev-requirements.txt

static-watch:
	npm run start

static-deploy:
	npm run deploy

serve:
	FLASK_APP=pokefight/app.py flask run --reload

lint:
	isort --check .
	black --check .

format:
	isort .
	black .
