# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-12 01:37
from __future__ import unicode_literals

from cardinal_pythonlib.django.fields.jsonclassfield import JsonClassField
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0003_patientexplorer_patientexploreraudit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientexplorer',
            name='patient_multiquery',
            field=JsonClassField(null=True, verbose_name='PatientMultiQuery as JSON'),  # noqa
        ),
        migrations.AlterField(
            model_name='query',
            name='args',
            field=JsonClassField(null=True, verbose_name='SQL arguments (as JSON)'),  # noqa
        ),
    ]
