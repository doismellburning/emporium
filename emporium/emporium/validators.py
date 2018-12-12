import requests
from django.core.exceptions import ValidationError


def validate_package_name_exists(name):
    resp = requests.get(
        "https://pypi.org/pypi/%s/json" % name,
        allow_redirects=False,  # PyPI will correct case with redirects, and argh
    )
    if resp.status_code != 200:
        raise ValidationError("%(name)s not found on PyPI", params={"name": name})
