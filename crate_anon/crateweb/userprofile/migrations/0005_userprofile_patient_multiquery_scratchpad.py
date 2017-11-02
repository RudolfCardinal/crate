# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-02-07 10:02
from __future__ import unicode_literals

from django.db import migrations
# noinspection PyPackageRequirements
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_userprofile_patients_per_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='patient_multiquery_scratchpad',
            field=picklefield.fields.PickledObjectField(editable=False, null=True, verbose_name='PatientMultiQuery scratchpad (pickled) for builder'),  # noqa
        ),
    ]
