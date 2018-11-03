#!/usr/bin/env python

"""
crate_anon/crateweb/consent/migrations/0010_auto_20180629_1238.py

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

**Consent app, migration 0011.**

"""

# Generated by Django 2.1.2 on 2018-10-22 08:01

import crate_anon.crateweb.consent.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consent', '0010_auto_20180629_1238'),
    ]

    # noinspection PyPep8
    operations = [
        migrations.AddField(
            model_name='study',
            name='summary_is_html',
            field=models.BooleanField(default=False, verbose_name='Is the summary in HTML (not plain text) format?'),
        ),
        migrations.AlterField(
            model_name='email',
            name='sender',
            field=models.CharField(default=crate_anon.crateweb.consent.models._get_default_email_sender, max_length=255),
        ),
    ]