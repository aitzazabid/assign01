# Generated by Django 3.2.9 on 2022-01-20 15:45

from django.db import migrations

from django.contrib.postgres import operations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_companycatgeory_productcategory'),
    ]

    operations = [
        operations.TrigramExtension(),
    ]
