# Generated by Django 2.2.1 on 2019-05-13 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0016_auto_20190513_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='name',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='slug',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
