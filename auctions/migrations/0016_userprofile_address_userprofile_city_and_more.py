# Generated by Django 4.1.2 on 2022-11-01 04:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_listing_paid_alter_comment_created_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='state',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 1, 4, 48, 50, 171241, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 1, 4, 48, 50, 172240, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 1, 4, 48, 50, 153243, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='profits',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 1, 4, 48, 50, 172240, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='sales',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 1, 4, 48, 50, 171241, tzinfo=datetime.timezone.utc)),
        ),
    ]
