# Generated by Django 3.0.8 on 2020-08-11 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_auto_20200810_0350'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='person',
            name='password',
            field=models.CharField(default="Not Set", max_length=128, verbose_name='password'),
            preserve_default=False,
        ),
    ]
