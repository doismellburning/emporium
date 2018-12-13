bootstrap-dev:
	pipenv install --dev

check:
	flake8 emporium
	black --check emporium
	isort --check-only --recursive emporium
	mypy emporium
	SECRET_KEY=notasecret emporium/manage.py makemigrations --check
	SECRET_KEY=notasecret emporium/manage.py check
	SECRET_KEY=notasecret-but-long-enough-for-Django-to-consider-it-secure emporium/manage.py check --deploy

fix:
	black emporium
	isort --apply --recursive emporium
	autopep8 --in-place --recursive emporium/

collectstatic:
	SECRET_KEY=notasecret emporium/manage.py collectstatic --noinput

test:
	SECRET_KEY=notasecret pytest emporium
