# Generated by Django 2.2.1 on 2019-05-06 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_auto_20190506_2213'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='html_extra_classes',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]