# Generated by Django 2.2.13 on 2020-11-02 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_auto_20201102_0044'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='refund_feedback',
            field=models.TextField(blank=True, null=True),
        ),
    ]