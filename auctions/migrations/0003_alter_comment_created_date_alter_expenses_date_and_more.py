# Generated by Django 4.1.2 on 2022-10-22 23:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_comment_created_date_alter_expenses_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 22, 23, 53, 23, 976210, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 22, 23, 53, 23, 977224, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 22, 23, 53, 23, 958211, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='profits',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 22, 23, 53, 23, 977224, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='sales',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 22, 23, 53, 23, 976210, tzinfo=datetime.timezone.utc)),
        ),
    ]