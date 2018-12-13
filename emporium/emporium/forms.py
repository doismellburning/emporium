from django.forms import ModelForm

from .models import Package


class PackageForm(ModelForm):
    class Meta:
        model = Package
        fields = ["name"]
