# Generated by Django 2.2.13 on 2020-12-07 03:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0040_auto_20201207_0210'),
        ('inkmail', '0012_message_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingmessage',
            name='journey_day',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.JourneyDay'),
        ),
    ]
