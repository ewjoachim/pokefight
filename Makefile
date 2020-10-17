isort:
	isort .

isort-check:
	isort -c .

black:
	black .

black-check:
	black --check .

lint: isort black

lint-check: isort-check black-check
