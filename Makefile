bootstrap-dev:
	pipenv install --dev

check:
	ruff check emporium
	black --check emporium
	mypy emporium
	SECRET_KEY=notasecret emporium/manage.py makemigrations --check
	SECRET_KEY=notasecret emporium/manage.py check
	SECRET_KEY=notasecret-but-long-enough-for-Django-to-consider-it-secure emporium/manage.py check --deploy

fix:
	black emporium
	ruff check --fix emporium

collectstatic:
	SECRET_KEY=notasecret emporium/manage.py collectstatic --noinput

test:
	SECRET_KEY=notasecret pytest emporium
