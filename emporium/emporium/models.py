from django.db import models


class Package(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class PackageVersion(models.Model):
    package = models.ForeignKey("package", on_delete=models.CASCADE)
    version = models.CharField(max_length=120)
    setuppy = models.TextField()
    fetched = models.BooleanField(default=False)

    def __str__(self):
        return str(self.package) + "-" + self.version
