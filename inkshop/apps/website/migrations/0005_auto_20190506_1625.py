# Generated by Django 2.2 on 2019-05-06 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20190506_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='hashid',
            field=models.CharField(blank=True, db_index=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='hashid',
            field=models.CharField(blank=True, db_index=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='template',
            name='hashid',
            field=models.CharField(blank=True, db_index=True, max_length=254, null=True),
        ),
    ]
