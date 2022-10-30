# Generated by Django 4.1.2 on 2022-10-25 03:27

import ckeditor.fields
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_comment_created_date_alter_expenses_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 3, 27, 28, 297274, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 3, 27, 28, 299246, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 3, 27, 28, 279283, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='profits',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 3, 27, 28, 298272, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='sales',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 25, 3, 27, 28, 297274, tzinfo=datetime.timezone.utc)),
        ),
    ]