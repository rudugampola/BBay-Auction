# Generated by Django 4.1.3 on 2022-11-20 17:47

from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0025_alter_listing_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='rmbg_image',
            field=models.ImageField(blank=True, null=True, upload_to='rmbg_image/'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, default='upload/placeholder.png', force_format=None, keep_meta=True, quality=100, scale=None, size=[300, 300], upload_to='upload/'),
        ),
    ]
