# Generated by Django 2.2.13 on 2020-11-11 00:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inkmail', '0010_organization_favicon'),
        ('products', '0027_productfeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='purchase_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inkmail.Message'),
        ),
        migrations.AddField(
            model_name='productpurchase',
            name='purchase_email_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productpurchase',
            name='purchase_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inkmail.OutgoingMessage'),
        ),
    ]
