# Generated by Django 2.2.13 on 2020-11-11 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inkmail', '0011_outgoingmessage_productpurchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='purchase',
            field=models.BooleanField(default=False),
        ),
    ]