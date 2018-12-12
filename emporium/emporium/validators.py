import requests
from django.core.exceptions import ValidationError


def validate_package_name_exists(name):
    resp = requests.get("https://pypi.org/pypi/%s/json" % name)
    if resp.status_code != 200:
        raise ValidationError("%(name)s not found on PyPI", params={"name": name})
