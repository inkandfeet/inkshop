# Generated by Django 2.2.13 on 2020-11-16 01:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0034_remove_bestimatoranswer_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bestimatoranswer',
            old_name='favorite_choice',
            new_name='experiment_choice',
        ),
    ]
