#!/usr/bin/env python

"""
crate_anon/crateweb/consent/migrations/0008_auto_20170507_1218.py

===============================================================================

    Copyright (C) 2015-2018 Rudolf Cardinal (rudolf@pobox.com).

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

**Consent app, migration 0008.**

"""
#  Generated by Django 1.10.5 on 2017-05-07 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consent', '0007_auto_20170228_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consentmode',
            name='consent_mode',
            field=models.CharField(choices=[('red', 'red'), ('yellow', 'yellow'), ('green', 'green')], default='', max_length=10, verbose_name='Consent mode (red/yellow/green)'),  # noqa
        ),
        migrations.AlterField(
            model_name='consentmode',
            name='source',
            field=models.CharField(default='crate_user_entry', max_length=20, verbose_name='Source of information'),  # noqa
        ),
        migrations.AlterField(
            model_name='leaflet',
            name='name',
            field=models.CharField(choices=[('cpft_tpir', 'CPFT: Taking part in research [MANDATORY]'), ('nihr_yhrsl', 'NIHR: Your health records save lives [not currently used]'), ('cpft_trafficlight_choice', 'CPFT: traffic-light choice decision form [not currently used: personalized version created instead]'), ('cpft_clinres', 'CPFT: clinical research [not currently used]')], max_length=50, unique=True, verbose_name='leaflet name'),  # noqa
        ),
    ]
