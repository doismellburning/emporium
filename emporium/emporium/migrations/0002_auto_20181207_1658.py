# Generated by Django 2.1.4 on 2018-12-07 16:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("emporium", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="package",
            name="name",
            field=models.CharField(max_length=120, unique=True),
        )
    ]
