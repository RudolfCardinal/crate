#!/usr/bin/env python

"""
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
"""

# Generated by Django 1.9.7 on 2016-06-21 15:11
from __future__ import unicode_literals

from cardinal_pythonlib.django.fields.restrictedcontentfile import ContentTypeRestrictedFileField  # noqa
import crate_anon.crateweb.consent.models
import crate_anon.crateweb.consent.storage
from django.db import migrations, models

# edited: FileField "location" defaults removed


class Migration(migrations.Migration):

    dependencies = [
        ('consent', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailattachment',
            name='file',
            field=models.FileField(storage=crate_anon.crateweb.consent.storage.CustomFileSystemStorage(base_url='download_privatestorage'), upload_to=''),  # noqa
        ),
        migrations.AlterField(
            model_name='leaflet',
            name='pdf',
            field=ContentTypeRestrictedFileField(blank=True, storage=crate_anon.crateweb.consent.storage.CustomFileSystemStorage(base_url='download_privatestorage'), upload_to=crate_anon.crateweb.consent.models.leaflet_upload_to),  # noqa
        ),
        migrations.AlterField(
            model_name='letter',
            name='pdf',
            field=models.FileField(storage=crate_anon.crateweb.consent.storage.CustomFileSystemStorage(base_url='download_privatestorage'), upload_to=''),  # noqa
        ),
        migrations.AlterField(
            model_name='study',
            name='study_details_pdf',
            field=ContentTypeRestrictedFileField(blank=True, storage=crate_anon.crateweb.consent.storage.CustomFileSystemStorage(base_url='download_privatestorage'), upload_to=crate_anon.crateweb.consent.models.study_details_upload_to),  # noqa
        ),
        migrations.AlterField(
            model_name='study',
            name='subject_form_template_pdf',
            field=ContentTypeRestrictedFileField(blank=True, storage=crate_anon.crateweb.consent.storage.CustomFileSystemStorage(base_url='download_privatestorage'), upload_to=crate_anon.crateweb.consent.models.study_form_upload_to),  # noqa
        ),
    ]
