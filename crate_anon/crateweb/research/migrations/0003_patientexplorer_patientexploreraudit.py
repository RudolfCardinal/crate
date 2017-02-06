# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-02-06 16:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('research', '0002_auto_20170203_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientExplorer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('patient_multiquery', picklefield.fields.PickledObjectField(editable=False, null=True, verbose_name='Pickled PatientMultiQuery')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False, verbose_name="Deleted from the user's perspective. Audited queries are never properly deleted.")),
                ('audited', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PatientExplorerAudit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('count_only', models.BooleanField(default=False)),
                ('n_records', models.IntegerField(default=0)),
                ('failed', models.BooleanField(default=False)),
                ('fail_msg', models.TextField()),
                ('patient_explorer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='research.PatientExplorer')),
            ],
        ),
    ]
