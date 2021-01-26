#!/usr/bin/env python

"""
crate_anon/crateweb/consent/migrations/0004_auto_20160703_1530.py

===============================================================================

    Copyright (C) 2015-2021 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of CRATE.

    CRATE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CRATE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CRATE. If not, see <http://www.gnu.org/licenses/>.

===============================================================================

**Consent app, migration 0004.**

"""

# Generated by Django 1.9.7 on 2016-07-03 15:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consent', '0003_auto_20160628_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='dummypatientsourceinfo',
            name='pt_discharge_date',
            field=models.DateField(blank=True, null=True, verbose_name='Patient date of discharge'),  # noqa
        ),
        migrations.AddField(
            model_name='patientlookup',
            name='pt_discharge_date',
            field=models.DateField(blank=True, null=True, verbose_name='Patient date of discharge'),  # noqa
        ),
    ]
