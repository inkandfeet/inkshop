# Generated by Django 2.2 on 2020-08-20 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_auto_20200811_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='encrypted_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]