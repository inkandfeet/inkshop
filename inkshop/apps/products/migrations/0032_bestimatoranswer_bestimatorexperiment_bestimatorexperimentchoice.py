# Generated by Django 2.2.13 on 2020-11-15 23:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0031_auto_20201113_0243'),
    ]

    operations = [
        migrations.CreateModel(
            name='BestimatorExperiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('hashid', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('name', models.CharField(max_length=512)),
                ('slug', models.CharField(blank=True, max_length=254, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(utils.models.DataDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BestimatorExperimentChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('hashid', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('name', models.CharField(max_length=512)),
                ('slug', models.CharField(blank=True, max_length=254, null=True)),
                ('url', models.CharField(blank=True, max_length=512, null=True)),
                ('pattern', models.CharField(blank=True, max_length=512, null=True)),
                ('template_name', models.CharField(blank=True, max_length=512, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(utils.models.DataDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BestimatorAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('hashid', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('name', models.CharField(max_length=512)),
                ('session_hash', models.CharField(max_length=512)),
                ('feels_grin', models.BooleanField(blank=True, null=True)),
                ('feels_laugh_cry', models.BooleanField(blank=True, null=True)),
                ('feels_love', models.BooleanField(blank=True, null=True)),
                ('feels_hmm', models.BooleanField(blank=True, null=True)),
                ('feels_embarrased', models.BooleanField(blank=True, null=True)),
                ('feels_shocked', models.BooleanField(blank=True, null=True)),
                ('feels_sick', models.BooleanField(blank=True, null=True)),
                ('feels_angry', models.BooleanField(blank=True, null=True)),
                ('authentic', models.BooleanField(blank=True, null=True)),
                ('good_value', models.BooleanField(blank=True, null=True)),
                ('interested_in_buying', models.BooleanField(blank=True, null=True)),
                ('other_comments', models.TextField(blank=True, null=True)),
                ('favorite_choice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.BestimatorExperimentChoice')),
            ],
            options={
                'abstract': False,
            },
            bases=(utils.models.DataDictMixin, models.Model),
        ),
    ]