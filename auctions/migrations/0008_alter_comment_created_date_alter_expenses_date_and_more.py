# Generated by Django 4.1.2 on 2022-10-25 04:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_alter_comment_created_date_alter_expenses_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 4, 43, 1, 383583, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 4, 43, 1, 384583, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 4, 43, 1, 367583, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.ImageField(default='https://bbay-auction.s3.us-west-1.amazonaws.com/media/profile/avatar.png', upload_to='upload/'),
        ),
        migrations.AlterField(
            model_name='profits',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 4, 43, 1, 384583, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='sales',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 4, 43, 1, 383583, tzinfo=datetime.timezone.utc)),
        ),
    ]
