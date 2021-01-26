#!/usr/bin/env python

"""
crate_anon/crateweb/research/migrations/0006_patientexplorer_pmq_hash.py

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

**Research app, migration 0006.**

"""

# Generated by Django 1.10.5 on 2017-02-17 00:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0005_query_sql_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientexplorer',
            name='pmq_hash',
            field=models.BigIntegerField(default=0, verbose_name='64-bit non-cryptographic hash of JSON of patient_multiquery'),  # noqa
            preserve_default=False,
        ),
    ]
