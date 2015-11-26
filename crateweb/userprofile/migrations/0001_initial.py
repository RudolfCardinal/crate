# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL, serialize=False, primary_key=True)),
                ('per_page', models.PositiveSmallIntegerField(default=50, choices=[(10, '10'), (20, '20'), (50, '50'), (100, '100'), (200, '200'), (500, '500'), (1000, '1000')], verbose_name='Number of items to show per page')),
                ('line_length', models.PositiveSmallIntegerField(default=80, verbose_name='Characters to word-wrap text at in results display (0 for no wrap)')),
                ('collapse_at', models.PositiveSmallIntegerField(default=400, verbose_name='Number of characters beyond which results field starts collapsed (0 for none)')),
                ('is_developer', models.BooleanField(default=False, verbose_name='Enable developer functions?')),
                ('title', models.CharField(max_length=20, blank=True)),
                ('address_1', models.CharField(max_length=100, blank=True, verbose_name='Address line 1')),
                ('address_2', models.CharField(max_length=100, blank=True, verbose_name='Address line 2')),
                ('address_3', models.CharField(max_length=100, blank=True, verbose_name='Address line 3')),
                ('address_4', models.CharField(max_length=100, blank=True, verbose_name='Address line 4')),
                ('address_5', models.CharField(max_length=100, blank=True, verbose_name='Address line 5 (county)')),
                ('address_6', models.CharField(max_length=100, blank=True, verbose_name='Address line 6 (postcode)')),
                ('address_7', models.CharField(max_length=100, blank=True, verbose_name='Address line 7 (country)')),
                ('telephone', models.CharField(max_length=20, blank=True)),
                ('is_consultant', models.BooleanField(default=False, verbose_name='User is an NHS consultant')),
                ('signatory_title', models.CharField(max_length=255, verbose_name='Title for signature (e.g. "Consultant psychiatrist")')),
            ],
        ),
    ]
