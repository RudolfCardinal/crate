#!/usr/bin/env python

"""
crate_anon/crateweb/research/migrations/0008_query_display.py

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

crate_anon/crateweb/research/migrations/0007_sitewidequery.py
**Research app, migration 0008.**

"""

# Generated by Django 2.1.2 on 2018-11-02 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0007_sitewidequery'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='display',
            field=models.TextField(default='[]', verbose_name='Subset of output columns to be displayed'),  # nopep8
        ),
    ]
