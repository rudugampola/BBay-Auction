# Generated by Django 4.1.3 on 2022-11-20 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0022_listing_listing_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='rmbg_img',
            field=models.ImageField(blank=True, upload_to='upload/rmbg/'),
        ),
    ]