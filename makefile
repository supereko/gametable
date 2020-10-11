lint:
	isort .
	pylint --rcfile=setup.cfg $(shell pwd)/apps

load_fixture:
	python manage.py loaddata $(shell pwd)/fixtures/cards.yaml

admin:
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell

ci_lint:
	isort . --df --check-only
	pylint-fail-under --rcfile=setup.cfg $(shell pwd)/apps
