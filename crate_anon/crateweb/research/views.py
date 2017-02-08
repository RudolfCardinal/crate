#!/usr/bin/env python
# crate_anon/crateweb/research/views.py

"""
===============================================================================
    Copyright (C) 2015-2017 Rudolf Cardinal (rudolf@pobox.com).

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

import datetime
from functools import lru_cache
import io
import json
import logging
from typing import Any, Dict, List, Union

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError,
)
from django.db import DatabaseError
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.html import escape
from openpyxl import Workbook
from pyparsing import ParseException

from crate_anon.common.contenttypes import (
    CONTENTTYPE_TSV,
    CONTENTTYPE_XLSX,
    CONTENTTYPE_ZIP,
)
from crate_anon.crateweb.core.dbfunc import (
    dictlist_to_tsv,
    escape_sql_string_literal,
    get_fieldnames_from_cursor,
)
from crate_anon.crateweb.core.utils import is_superuser, paginate
from crate_anon.crateweb.extra.serve import file_response
from crate_anon.crateweb.research.forms import (
    AddHighlightForm,
    AddQueryForm,
    PidLookupForm,
    QueryBuilderForm,
    SQLHelperTextAnywhereForm,
)
from crate_anon.crateweb.research.html_functions import (
    highlight_text,
    HtmlElementCounter,
    make_result_element,
    make_collapsible_sql_query,
    N_CSS_HIGHLIGHT_CLASSES,
    pre,
    prettify_sql_css,
    prettify_sql_html,
)
from crate_anon.crateweb.research.models import (
    Highlight,
    PidLookup,
    PatientExplorer,
    PatientMultiQuery,
    Query,
)
from crate_anon.crateweb.research.research_db_info import (
    get_default_database,
    get_default_schema,
    get_researchdb_databases_schemas,
    is_db_schema_eligible_for_query_builder,
    get_schema_trid_field,
    get_schema_rid_field,
    research_database_info,
)
from crate_anon.crateweb.userprofile.models import get_patients_per_page
from crate_anon.common.sql import (
    ColumnId,
    SQL_OPS_MULTIPLE_VALUES,
    SQL_OPS_VALUE_UNNECESSARY,
    toggle_distinct,
    WhereCondition,
)
from crate_anon.common.sql_grammar import (
    DIALECT_MYSQL,
    DIALECT_MSSQL,
    make_grammar,
)
from crate_anon.crateweb.research.sql_writer import add_to_select

log = logging.getLogger(__name__)


# =============================================================================
# Helper functions
# =============================================================================

def validate_blank_form(request: HttpRequest) -> None:
    """
    Checks that the request is (a) a POST request, and (b) passes CRSF
    validation.
    """
    if request.method != "POST":
        raise ValidationError("Use HTTP POST, not HTTP GET or other methods")
    form = forms.Form(request.POST)
    if not form.is_valid():  # checks CSRF
        raise ValidationError("Form failed validation")


def query_context(request: HttpRequest) -> Dict[str, Any]:
    query_id = Query.get_active_query_id_or_none(request)
    pe_id = PatientExplorer.get_active_pe_id_or_none(request)
    return {
        'query_selected': query_id is not None,
        'current_query_id': query_id,
        'pe_selected': pe_id is not None,
        'current_pe_id': pe_id,
    }
    # Try to minimize SQL here, as these calls will be used for EVERY
    # request.
    # This problem can be circumvented with a per-request cache; see
    # http://stackoverflow.com/questions/3151469/per-request-cache-in-django


def datetime_iso_for_filename() -> str:
    dtnow = datetime.datetime.now()
    return dtnow.strftime("%Y%m%d_%H%M%S")


# =============================================================================
# Queries
# =============================================================================

@lru_cache(maxsize=None)
def get_db_structure_json() -> str:
    colinfolist = research_database_info.get_colinfolist()
    if not colinfolist:
        log.warning("get_db_structure_json(): colinfolist is empty")
    info = []
    for db, schema in get_researchdb_databases_schemas():  # preserve order  # noqa
        log.info("get_db_structure_json: db {}, schema {}".format(
            repr(db), repr(schema)))
        if not is_db_schema_eligible_for_query_builder(db, schema):
            log.debug("Skipping db={}, schema={}: not eligible for query "
                      "builder".format(repr(db), repr(schema)))
            continue
        schema_cil = [x for x in colinfolist
                      if x.table_catalog == db and x.table_schema == schema]
        trid_field = get_schema_trid_field(db, schema)
        rid_field = get_schema_rid_field(db, schema)
        table_info = []
        for table in sorted(set(x.table_name for x in schema_cil)):
            table_cil = [x for x in schema_cil if x.table_name == table]
            if not any(x for x in table_cil
                       if x.column_name == trid_field):
                # This table doesn't contain a TRID, so we will skip it.
                log.debug("... skipping table {}: no TRID [{}]".format(
                    table, trid_field))
                continue
            if not any(x for x in table_cil
                       if x.column_name == rid_field):
                # This table doesn't contain a RID, so we will skip it.
                log.debug("... skipping table {}: no RID [{}]".format(
                    table, rid_field))
                continue
            column_info = []
            for ci in sorted(table_cil, key=lambda x: x.column_name):
                column_info.append({
                    'colname': ci.column_name,
                    'coltype': ci.querybuilder_type(),
                    'rawtype': ci.column_type,
                    'comment': ci.column_comment or '',
                })
            if column_info:
                table_info.append({
                    'table': table,
                    'columns': column_info,
                })
            log.debug("... using table {}: {} columns".format(
                table, len(column_info)))
        if table_info:
            info.append({
                'database': db,
                'schema': schema,
                'tables': table_info,
            })
    return json.dumps(info)


def query_build(request: HttpRequest) -> HttpResponse:
    """
    Assisted query builder, based on the data dictionary.
    """
    # NOTES FOR FIRST METHOD, with lots (and lots) of forms.
    # - In what follows, we want a normal template but we want to include a
    #   large chunk of raw HTML. I was doing this with
    #   {{ builder_html | safe }} within the template, but it was very slow
    #   (e.g. 500ms on my machine; 50s on the CPFT "sandpit" server,
    #   2016-06-28). The delay was genuinely in the template rendering, it
    #   seems, based on profiling and manual log calls.
    # - A simple string replacement, as below, was about 7% of the total time
    #   (e.g. 3300ms instead of 50s).
    # - Other alternatives might include the Jinja2 template system, which is
    #   apparently faster than the Django default, but we may not need further
    #   optimization.
    # - Another, potentially better, solution, is not to send dozens or
    #   hundreds of forms, but to write some Javascript to make this happen
    #   mostly on the client side. Might look better, too. (Yes, it does.)

    # NB: first "submit" button takes the Enter key, so place WHERE
    # before SELECT so users can hit enter in the WHERE value fields.

    # - If you provide the "request=request" argument to
    #   render_to_string it gives you the CSRF token.
    # - Another way is to ignore "request" and use render_to_string
    #   with a manually crafted context including 'csrf_token'.
    #   (This avoids the global context processors.)
    # - Note that the CSRF token prevents simple caching of the forms.
    # - But we can't cache anyway if we're going to have some forms
    #   (differentially) non-collapsed at the start, e.g. on form POST.
    # - Also harder work to do this HTML manually (rather than with
    #   template rendering), because the csrf_token ends up like:
    #   <input type='hidden' name='csrfmiddlewaretoken' value='RGN5UZnTVkLFAVNtXRpJwn5CclBRAdLr' />  # noqa

    profile = request.user.profile
    parse_error = ''
    default_database = get_default_database()
    default_schema = get_default_schema()
    with_database = research_database_info.uses_database_level()
    form = None

    if request.method == 'POST':
        grammar = make_grammar(settings.RESEARCH_DB_DIALECT)
        try:
            if 'global_clear' in request.POST:
                profile.sql_scratchpad = ''
                profile.save()

            elif 'global_toggle_distinct' in request.POST:
                profile.sql_scratchpad = toggle_distinct(
                    profile.sql_scratchpad,
                    dialect=settings.RESEARCH_DB_DIALECT)
                profile.save()

            elif 'global_save' in request.POST:
                return query_submit(request, profile.sql_scratchpad, run=False)

            elif 'global_run' in request.POST:
                return query_submit(request, profile.sql_scratchpad, run=True)

            else:
                form = QueryBuilderForm(request.POST, request.FILES)
                if form.is_valid():
                    # log.critical("is_valid")
                    database = (form.cleaned_data['database'] if with_database
                                else '')
                    schema = form.cleaned_data['schema']
                    table = form.cleaned_data['table']
                    column = form.cleaned_data['column']
                    column_id = ColumnId(db=database, schema=schema,
                                         table=table, column=column)
                    table_id = column_id.table_id()

                    if 'submit_select' in request.POST:
                        profile.sql_scratchpad = add_to_select(
                            profile.sql_scratchpad,
                            select_column=column_id,
                            magic_join=True,
                            dialect=settings.RESEARCH_DB_DIALECT
                        )

                    elif 'submit_where' in request.POST:
                        datatype = form.cleaned_data['datatype']
                        op = form.cleaned_data['where_op']
                        # Value
                        if op in SQL_OPS_MULTIPLE_VALUES:
                            value = form.file_values_list
                        elif op in SQL_OPS_VALUE_UNNECESSARY:
                            value = None
                        else:
                            value = form.get_cleaned_where_value()
                        # WHERE fragment
                        wherecond = WhereCondition(column_id=column_id,
                                                   op=op,
                                                   datatype=datatype,
                                                   value_or_values=value)
                        profile.sql_scratchpad = add_to_select(
                            profile.sql_scratchpad,
                            where_type="AND",
                            where_expression=wherecond.sql(grammar),
                            where_table=table_id,
                            magic_join=True,
                            dialect=settings.RESEARCH_DB_DIALECT
                        )

                    else:
                        raise ValueError("Bad form command!")
                    profile.save()

                else:
                    # log.critical("not is_valid")
                    pass

        except ParseException as e:
            parse_error = str(e)

    if form is None:
        form = QueryBuilderForm()

    starting_values_dict = {
        'database': form.data.get('database', '') if with_database else '',
        'schema': form.data.get('schema', ''),
        'table': form.data.get('table', ''),
        'column': form.data.get('column', ''),
        'op': form.data.get('where_op', ''),
        'date_value': form.data.get('date_value', ''),
        # Impossible to set file_value programmatically. (See querybuilder.js.)
        'float_value': form.data.get('float_value', ''),
        'int_value': form.data.get('int_value', ''),
        'string_value': form.data.get('string_value', ''),
        'offer_where': bool(profile.sql_scratchpad),  # existing SELECT?
        'form_errors': "<br>".join("{}: {}".format(k, v)
                                   for k, v in form.errors.items()),
        'default_database': default_database,
        'default_schema': default_schema,
        'with_database': with_database,
    }
    context = {
        'nav_on_querybuilder': True,
        'sql': prettify_sql_html(profile.sql_scratchpad),
        'parse_error': parse_error,
        'database_structure': get_db_structure_json(),
        'starting_values': json.dumps(starting_values_dict),
        'sql_dialect': settings.RESEARCH_DB_DIALECT,
        'dialect_mysql': settings.RESEARCH_DB_DIALECT == DIALECT_MYSQL,
        'dialect_mssql': settings.RESEARCH_DB_DIALECT == DIALECT_MSSQL,
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'query_build.html', context)


def get_all_queries(request: HttpRequest) -> QuerySet:
    return Query.objects.filter(user=request.user, deleted=False)\
                        .order_by('-active', '-created')


def query_submit(request: HttpRequest,
                 sql: str,
                 run: bool = False) -> HttpResponse:
    """
    Ancillary function to add a query, and redirect to the editing or
    run page.
    """
    all_queries = get_all_queries(request)
    identical_queries = all_queries.filter(sql=sql)
    # - 2017-02-03: we had a problem here, in which the parameter was sent to
    #   SQL Server as type NTEXT, but the field "sql" is NVARCHAR(MAX), leading
    #   to "The data types nvarchar(max) and ntext are incompatible in the
    #   equal to operator."
    # - The Django field type TextField is converted to NVARCHAR(MAX) by
    #   django-pyodbc-azure, in sql_server/pyodbc/base.py, also at
    #   https://github.com/michiya/django-pyodbc-azure/blob/azure-1.10/sql_server/pyodbc/base.py  # noqa
    # - Error is reproducible with
    #       ... WHERE sql = CAST('hello' AS NTEXT) ...
    # - The order of the types in the error message matches the order in the
    #   SQL statement.
    # - A solution would be to cast the parameter as
    #   CAST(some_parameter AS NVARCHAR(MAX))
    # - Fixed by upgrading pyodbc from 3.1.1 to 4.0.3
    # - Added to FAQ
    if identical_queries:
        identical_queries[0].activate()
        query_id = identical_queries[0].id
    else:
        query = Query(sql=sql, raw=True, user=request.user,
                      active=True)
        query.save()
        query_id = query.id
    # redirect to a new URL:
    if run:
        return redirect('results', query_id)
    else:
        return redirect('query')


def query_edit_select(request: HttpRequest) -> HttpResponse:
    """
    Edit or select SQL for current query.
    """
    # log.debug("query")
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddQueryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            cmd_run = 'submit_run' in request.POST
            cmd_add = 'submit_add' in request.POST
            cmd_builder = 'submit_builder' in request.POST
            # process the data in form.cleaned_data as required
            sql = form.cleaned_data['sql']
            if cmd_add or cmd_run:
                run = 'submit_run' in request.POST
                return query_submit(request, sql, run)
            elif cmd_builder:
                profile = request.user.profile
                profile.sql_scratchpad = sql
                profile.save()
                return redirect('build_query')
            else:
                raise ValueError("Bad command!")

    # if a GET (or any other method) we'll create a blank form
    values = {}
    all_queries = get_all_queries(request)
    active_queries = all_queries.filter(active=True)
    if active_queries:
        values['sql'] = active_queries[0].get_original_sql()
    form = AddQueryForm(values)
    queries = paginate(request, all_queries)
    profile = request.user.profile
    element_counter = HtmlElementCounter()
    for q in queries:
        q.formatted_query_safe = make_collapsible_sql_query(
            q.get_original_sql(),
            element_counter=element_counter,
            collapse_at_n_lines=profile.collapse_at_n_lines,
        )
        element_counter.next()
    context = {
        'form': form,
        'queries': queries,
        'nav_on_query': True,
        'dialect_mysql': settings.RESEARCH_DB_DIALECT == DIALECT_MYSQL,
        'dialect_mssql': settings.RESEARCH_DB_DIALECT == DIALECT_MSSQL,
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'query_edit_select.html', context)


def query_activate(request: HttpRequest, query_id: int) -> HttpResponse:
    validate_blank_form(request)
    query = get_object_or_404(Query, id=query_id)  # type: Query
    query.activate()
    return redirect('query')


def query_delete(request: HttpRequest, query_id: int) -> HttpResponse:
    validate_blank_form(request)
    query = get_object_or_404(Query, id=query_id)  # type: Query
    query.delete_if_permitted()
    return redirect('query')


def no_query_selected(request: HttpRequest) -> HttpResponse:
    return render(request, 'query_none_selected.html', query_context(request))


def query_count(request: HttpRequest, query_id: int) -> HttpResponse:
    """
    View COUNT(*) from specific query.
    """
    if query_id is None:
        return no_query_selected(request)
    try:
        query_id = int(query_id)
        # ... conceivably might raise TypeError (from e.g. None), ValueError
        # (from e.g. "xyz"), but both should be filtered out by the URL parser
        query = Query.objects.get(id=query_id, user=request.user)
        # ... will return None if not found, but may raise something derived
        # from ObjectDoesNotExist or (in principle, if this weren't a PK)
        # MultipleObjectsReturned;
        # https://docs.djangoproject.com/en/1.9/ref/models/querysets/#django.db.models.query.QuerySet.get  # noqa
    except ObjectDoesNotExist:
        return render_bad_query_id(request, query_id)
    return render_resultcount(request, query)


def query_count_current(request: HttpRequest) -> HttpResponse:
    """
    View COUNT(*) from current query.
    """
    query = Query.get_active_query_or_none(request)
    if query is None:
        return no_query_selected(request)
    return render_resultcount(request, query)


def query_results(request: HttpRequest, query_id: int) -> HttpResponse:
    """
    View results of chosen query, in tabular format
    """
    if query_id is None:
        return no_query_selected(request)
    try:
        query_id = int(query_id)
        query = Query.objects.get(id=query_id, user=request.user)
    except ObjectDoesNotExist:
        return render_bad_query_id(request, query_id)
    profile = request.user.profile
    highlights = Highlight.get_active_highlights(request)
    return render_resultset(request, query, highlights,
                            collapse_at_len=profile.collapse_at_len,
                            collapse_at_n_lines=profile.collapse_at_n_lines,
                            line_length=profile.line_length)


def query_results_recordwise(request: HttpRequest,
                             query_id: int) -> HttpResponse:
    """
    View results of chosen query, in tabular format
    """
    if query_id is None:
        return no_query_selected(request)
    try:
        query_id = int(query_id)
        query = Query.objects.get(id=query_id, user=request.user)
    except ObjectDoesNotExist:
        return render_bad_query_id(request, query_id)
    profile = request.user.profile
    highlights = Highlight.get_active_highlights(request)
    return render_resultset_recordwise(
        request, query, highlights,
        collapse_at_len=profile.collapse_at_len,
        collapse_at_n_lines=profile.collapse_at_n_lines,
        line_length=profile.line_length)


def query_tsv(request: HttpRequest, query_id: int) -> HttpResponse:
    """
    Download TSV of current query.
    """
    query = get_object_or_404(Query, id=query_id)  # type: Query
    try:
        tsv_result = query.make_tsv()
        filename = "crate_results_{num}_{datetime}.tsv".format(
            num=query.id,
            datetime=datetime_iso_for_filename(),
        )
        return tsv_response(tsv_result, filename=filename)
    except DatabaseError as exception:
        return render_bad_query(request, query, exception)


def query_excel(request: HttpRequest, query_id: int) -> HttpResponse:
    query = get_object_or_404(Query, id=query_id)  # type: Query
    wb = Workbook()
    wb.remove_sheet(wb.active)  # remove the autocreated blank sheet
    sheetname = "query_{num}_{datetime}".format(
        num=query.id,
        datetime=datetime_iso_for_filename())
    try:
        query.add_excel_sheet(wb, title=sheetname)
        sql_ws = wb.create_sheet(title="SQL")
        sql_ws.append(query.get_original_sql())
        memfile = io.BytesIO()
        wb.save(memfile)
        return HttpResponse(memfile.getvalue(), content_type=CONTENTTYPE_XLSX)
    except DatabaseError as exception:
        return render_bad_query(request, query, exception)


# @user_passes_test(is_superuser)
# def audit(request):
#     """
#     View audit log
#     """
#     all_audits = QueryAudit.objects.all()\
#                                    .select_related('query', 'query__user')\
#                                    .order_by('-id')
#     audits = paginate(request, all_audits)
#     context = {'audits': audits}
#     return render(request, 'audit.html', context)


# =============================================================================
# Internal functions for views on queries
# =============================================================================

# def make_demo_query_unless_exists(request):
#     DEMOQUERY = Query(
#         pk=1,
#         sql="SELECT * FROM notes\nWHERE note LIKE '%Adam%'\nLIMIT 20",
#         raw=True,
#         user=request.user,
#     )
#     DEMOQUERY.save()
#     H1 = Highlight(pk=1, text="Aaron", colour=0, user=request.user)
#     H1.save()
#     H2 = Highlight(pk=2, text="Adam", colour=0, user=request.user)
#     H2.save()
#     H3 = Highlight(pk=3, text="October", colour=1, user=request.user)
#     H3.save()

# EXCEPTIONS FOR HOMEBREW SQL.
# You can see:
# - django.db.ProgrammingError
# - django.db.OperationalError
# - InternalError (?django.db.utils.InternalError)
# ... but I think all are subclasses of django.db.utils.DatabaseError


def render_resultcount(request: HttpRequest, query: Query) -> HttpResponse:
    """
    Displays the number of rows that a given query will fetch.
    """
    if query is None:
        return render_missing_query(request)
    try:
        with query.get_executed_cursor() as cursor:
            rowcount = cursor.rowcount
        query.audit(count_only=True, n_records=rowcount)
        context = {
            'rowcount': rowcount,
            'sql': query.get_original_sql(),
            'nav_on_count': True,
        }
        context.update(query_context(request))
        return render(request, 'query_count.html', context)
    # See above re exception classes
    except DatabaseError as exception:
        query.audit(count_only=True, failed=True,
                    fail_msg=str(exception))
        return render_bad_query(request, query, exception)


def resultset_html_table(fieldnames: List[str],
                         rows: List[List[Any]],
                         element_counter: HtmlElementCounter,
                         start_index: int = 0,
                         highlight_dict: Dict[int, List[Highlight]] = None,
                         collapse_at_len: int = None,
                         collapse_at_n_lines: int = None,
                         line_length: int = None,
                         ditto: bool = True,
                         ditto_html: str = '″') -> str:
    ditto_cell = '    <td class="queryresult ditto">{}</td>\n'.format(
        ditto_html)

    html = '<table>\n'
    html += '  <tr>\n'
    html += '    <th><i>#</i></th>\n'
    for field in fieldnames:
        html += '    <th>{}</th>\n'.format(escape(field))
    html += '  </tr>\n'
    for row_index, row in enumerate(rows):
        # row_index is zero-based within this table
        html += '  <tr class="{}">\n'.format(
            "stripy_even" if row_index % 2 == 0 else "stripy_odd"
        )
        # Row number
        html += '    <td><b><i>{}</i></b></td>\n'.format(
            row_index + start_index + 1)
        # Values
        for col_index, value in enumerate(row):
            if (row_index > 0 and ditto and
                    value == rows[row_index - 1][col_index]):
                html += ditto_cell
            else:
                html += '    <td class="queryresult">{}</td>\n'.format(
                    make_result_element(
                        value,
                        element_counter=element_counter,
                        highlight_dict=highlight_dict,
                        collapse_at_len=collapse_at_len,
                        collapse_at_n_lines=collapse_at_n_lines,
                        line_length=line_length
                    )
                )
            element_counter.next()
        html += '  </tr>\n'
    html += '</table>\n'
    return html


def single_record_html_table(fieldnames: List[str],
                             record: List[Any],
                             element_counter: HtmlElementCounter,
                             highlight_dict: Dict[int, List[Highlight]] = None,
                             collapse_at_len: int = None,
                             collapse_at_n_lines: int = None,
                             line_length: int = None) -> str:
    table_html = '<table>\n'
    for col_index, value in enumerate(record):
        fieldname = fieldnames[col_index]
        table_html += '  <tr class="{}">\n'.format(
            "stripy_even" if col_index % 2 == 0 else "stripy_odd"
        )
        table_html += '    <th>{}</th>'.format(escape(fieldname))
        table_html += (
            '    <td class="queryresult">{}</td>\n'.format(
                make_result_element(
                    value,
                    element_counter=element_counter,
                    highlight_dict=highlight_dict,
                    collapse_at_len=collapse_at_len,
                    collapse_at_n_lines=collapse_at_n_lines,
                    line_length=line_length,
                    collapsed=False,
                )
            )
        )
        element_counter.next()
        table_html += '  </tr>\n'
    table_html += '</table>\n'
    return table_html


def render_resultset(request: HttpRequest,
                     query: Query,
                     highlights: Union[QuerySet, List[Highlight]],
                     collapse_at_len: int = None,
                     collapse_at_n_lines: int = None,
                     line_length: int = None,
                     ditto: bool = True,
                     ditto_html: str = '″') -> HttpResponse:
    # Query
    if query is None:
        return render_missing_query(request)
    try:
        with query.get_executed_cursor() as cursor:
            rowcount = cursor.rowcount
            query.audit(n_records=rowcount)
            fieldnames = get_fieldnames_from_cursor(cursor)
            rows = cursor.fetchall()
    except DatabaseError as exception:
        query.audit(failed=True, fail_msg=str(exception))
        return render_bad_query(request, query, exception)
    row_indexes = list(range(len(rows)))
    # We don't need to process all rows before we paginate.
    page = paginate(request, row_indexes)
    start_index = page.start_index() - 1
    end_index = page.end_index() - 1
    display_rows = rows[start_index:end_index + 1]
    # Highlights
    highlight_dict = Highlight.as_ordered_dict(highlights)
    highlight_descriptions = get_highlight_descriptions(highlight_dict)
    # Table
    element_counter = HtmlElementCounter()
    table_html = resultset_html_table(
        fieldnames=fieldnames,
        rows=display_rows,
        element_counter=element_counter,
        start_index=start_index,
        highlight_dict=highlight_dict,
        collapse_at_len=collapse_at_len,
        collapse_at_n_lines=collapse_at_n_lines,
        line_length=line_length,
        ditto=ditto,
        ditto_html=ditto_html,
    )
    # Render
    context = {
        'fieldnames': fieldnames,
        'highlight_descriptions': highlight_descriptions,
        'table_html': table_html,
        'page': page,
        'rowcount': rowcount,
        'sql': prettify_sql_html(query.get_original_sql()),
        'nav_on_results': True,
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'query_result.html', context)


def render_resultset_recordwise(request: HttpRequest,
                                query: Query,
                                highlights: Union[QuerySet, List[Highlight]],
                                collapse_at_len: int = None,
                                collapse_at_n_lines: int = None,
                                line_length: int = None) -> HttpResponse:
    # Query
    if query is None:
        return render_missing_query(request)
    try:
        with query.get_executed_cursor() as cursor:
            rowcount = cursor.rowcount
            query.audit(n_records=rowcount)
            fieldnames = get_fieldnames_from_cursor(cursor)
            rows = cursor.fetchall()
    except DatabaseError as exception:
        query.audit(failed=True, fail_msg=str(exception))
        return render_bad_query(request, query, exception)
    row_indexes = list(range(len(rows)))
    # We don't need to process all rows before we paginate.
    page = paginate(request, row_indexes, per_page=1)
    # Highlights
    highlight_dict = Highlight.as_ordered_dict(highlights)
    highlight_descriptions = get_highlight_descriptions(highlight_dict)
    if rows:
        record_index = page.start_index() - 1
        record = rows[record_index]
        # Table
        element_counter = HtmlElementCounter()
        table_html = '<p><i>Record {}</i></p>\n'.format(page.start_index())
        table_html += single_record_html_table(
            fieldnames=fieldnames,
            record=record,
            element_counter=element_counter,
            highlight_dict=highlight_dict,
            collapse_at_len=collapse_at_len,
            collapse_at_n_lines=collapse_at_n_lines,
            line_length=line_length,
        )
    else:
        table_html = "<b>No rows returned.</b>"
    # Render
    context = {
        'fieldnames': fieldnames,
        'highlight_descriptions': highlight_descriptions,
        'table_html': table_html,
        'page': page,
        'rowcount': rowcount,
        'sql': prettify_sql_html(query.get_original_sql()),
        'nav_on_results_recordwise': True,
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'query_result.html', context)


def tsv_response(data: str, filename: str = "download.tsv") -> HttpResponse:
    # http://stackoverflow.com/questions/264256/what-is-the-best-mime-type-and-extension-to-use-when-exporting-tab-delimited  # noqa
    # http://www.iana.org/assignments/media-types/text/tab-separated-values
    return file_response(data, content_type=CONTENTTYPE_TSV, filename=filename)


def render_missing_query(request: HttpRequest) -> HttpResponse:
    return render(request, 'query_missing.html', query_context(request))


def render_bad_query(request: HttpRequest,
                     query: Query,
                     exception: Exception) -> HttpResponse:
    (final_sql, args) = query.get_sql_args_for_mysql()
    context = {
        'original_sql': prettify_sql_html(query.get_original_sql()),
        'final_sql': prettify_sql_html(final_sql),
        'args': str(args),
        'exception': str(exception),
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'query_bad.html', context)


def render_bad_query_id(request: HttpRequest, query_id: int) -> HttpResponse:
    context = {'query_id': query_id}
    context.update(query_context(request))
    return render(request, 'query_bad_id.html', context)


# =============================================================================
# Highlights
# =============================================================================

def highlight_edit_select(request: HttpRequest) -> HttpResponse:
    """
    Edit or select highlighting for current query.
    """
    all_highlights = Highlight.objects.filter(user=request.user)\
                                      .order_by('text', 'colour')
    if request.method == 'POST':
        form = AddHighlightForm(request.POST)
        if form.is_valid():
            colour = form.cleaned_data['colour']
            text = form.cleaned_data['text']
            identicals = all_highlights.filter(colour=colour, text=text)
            if identicals:
                identicals[0].activate()
            else:
                highlight = Highlight(colour=colour, text=text,
                                      user=request.user, active=True)
                highlight.save()
            return redirect('highlight')

    values = {'colour': 0}
    form = AddHighlightForm(values)
    active_highlights = all_highlights.filter(active=True)
    highlight_dict = Highlight.as_ordered_dict(active_highlights)
    highlight_descriptions = get_highlight_descriptions(highlight_dict)
    highlights = paginate(request, all_highlights)
    context = {
        'form': form,
        'highlights': highlights,
        'nav_on_highlight': True,
        'N_CSS_HIGHLIGHT_CLASSES': N_CSS_HIGHLIGHT_CLASSES,
        'highlight_descriptions': highlight_descriptions,
        'colourlist': list(range(N_CSS_HIGHLIGHT_CLASSES)),
    }
    context.update(query_context(request))
    return render(request, 'highlight_edit_select.html', context)


def highlight_activate(request: HttpRequest,
                       highlight_id: int) -> HttpResponse:
    validate_blank_form(request)
    highlight = get_object_or_404(Highlight, id=highlight_id)  # type: Highlight
    highlight.activate()
    return redirect('highlight')


def highlight_deactivate(request: HttpRequest,
                         highlight_id: int) -> HttpResponse:
    validate_blank_form(request)
    highlight = get_object_or_404(Highlight, id=highlight_id)  # type: Highlight
    highlight.deactivate()
    return redirect('highlight')


def highlight_delete(request: HttpRequest,
                     highlight_id: int) -> HttpResponse:
    validate_blank_form(request)
    highlight = get_object_or_404(Highlight, id=highlight_id)  # type: Highlight
    highlight.delete()
    return redirect('highlight')


# def render_bad_highlight_id(request, highlight_id):
#     context = {'highlight_id': highlight_id}
#     context.update(query_context(request))
#     return render(request, 'highlight_bad_id.html', context)


def get_highlight_descriptions(
        highlight_dict: Dict[int, List[Highlight]]) -> List[str]:
    """
    Returns a list of length up to N_CSS_HIGHLIGHT_CLASSES of HTML
    elements illustrating the highlights.
    """
    desc = []
    for n in range(N_CSS_HIGHLIGHT_CLASSES):
        if n not in highlight_dict:
            continue
        desc.append(", ".join([highlight_text(h.text, n)
                               for h in highlight_dict[n]]))
    return desc


# =============================================================================
# PID lookup
# =============================================================================

def pidlookup(request: HttpRequest) -> HttpResponse:
    """
    Look up PID information from RID information.
    """
    form = PidLookupForm(request.POST or None)
    if form.is_valid():
        trids = form.cleaned_data['trids']
        rids = form.cleaned_data['rids']
        mrids = form.cleaned_data['mrids']
        return render_lookup(request, trids=trids, rids=rids, mrids=mrids)
    return render(request, 'pid_lookup_form.html', {'form': form})


@user_passes_test(is_superuser)
def render_lookup(request: HttpRequest,
                  trids: List[int] = None,
                  rids: List[str] = None,
                  mrids: List[str] = None,
                  pids: List[int] = None,
                  mpids: List[int] = None) -> HttpResponse:
    # if not request.user.superuser:
    #    return HttpResponse('Forbidden', status=403)
    #    # http://stackoverflow.com/questions/3297048/403-forbidden-vs-401-unauthorized-http-responses  # noqa
    trids = [] if trids is None else trids
    rids = [] if rids is None else rids
    mrids = [] if mrids is None else mrids
    pids = [] if pids is None else pids
    mpids = [] if mpids is None else mpids
    lookups = PidLookup.objects.filter(
        Q(trid__in=trids) |
        Q(rid__in=rids) |
        Q(mrid__in=mrids) |
        Q(pid__in=pids) |
        Q(mpid__in=mpids)
    ).order_by('pid')
    context = {
        'lookups': lookups,
        'SECRET_MAP': settings.SECRET_MAP,
    }
    return render(request, 'pid_lookup_result.html', context)


# =============================================================================
# Research database structure
# =============================================================================

def structure_table_long(request: HttpRequest) -> HttpResponse:
    colinfolist = research_database_info.get_colinfolist()
    rowcount = len(colinfolist)
    context = {
        'paginated': False,
        'colinfolist': colinfolist,
        'rowcount': rowcount,
        'default_database': get_default_database(),
        'default_schema': get_default_schema(),
        'with_database': research_database_info.uses_database_level(),
    }
    return render(request, 'database_structure.html', context)


def structure_table_paginated(request: HttpRequest) -> HttpResponse:
    colinfolist = research_database_info.get_colinfolist()
    rowcount = len(colinfolist)
    colinfolist = paginate(request, colinfolist)
    context = {
        'paginated': True,
        'colinfolist': colinfolist,
        'rowcount': rowcount,
        'default_database': get_default_database(),
        'default_schema': get_default_schema(),
        'with_database': research_database_info.uses_database_level(),
    }
    return render(request, 'database_structure.html', context)


@lru_cache(maxsize=None)
def get_structure_tree_html() -> str:
    table_to_colinfolist = research_database_info.get_colinfolist_by_tables()
    content = ""
    element_counter = HtmlElementCounter()
    grammar = make_grammar(settings.RESEARCH_DB_DIALECT)
    for table_id, colinfolist in table_to_colinfolist:
        html_table = render_to_string(
            'database_structure_table.html', {
                'colinfolist': colinfolist,
                'default_database': get_default_database(),
                'default_schema': get_default_schema(),
                'with_database': research_database_info.uses_database_level()
            })
        cd_button = element_counter.collapsible_div_spanbutton()
        cd_content = element_counter.collapsible_div_contentdiv(
            contents=html_table)
        content += (
            '<div class="titlecolour">{button} {db_schema}.<b>{table}</b></div>'
            '{cd}'.format(
                db_schema=table_id.database_schema_part(grammar),
                table=table_id.table_part(grammar),
                button=cd_button,
                cd=cd_content,
            )
        )
    return content


def structure_tree(request: HttpRequest) -> HttpResponse:
    context = {
        'content': get_structure_tree_html(),
        'default_database': get_default_database(),
        'default_schema': get_default_schema(),
    }
    return render(request, 'database_structure_tree.html', context)


# noinspection PyUnusedLocal
def structure_tsv(request: HttpRequest) -> HttpResponse:
    infodictlist = research_database_info.get_infodictlist()
    tsv_result = dictlist_to_tsv(infodictlist)
    return tsv_response(tsv_result, filename="structure.tsv")


# =============================================================================
# Local help on structure
# =============================================================================

def local_structure_help(request: HttpRequest) -> HttpResponse:
    if settings.DATABASE_HELP_HTML_FILENAME:
        with open(settings.DATABASE_HELP_HTML_FILENAME, 'r') as infile:
            content = infile.read()
            return HttpResponse(content.encode('utf8'))
    else:
        content = "<p>No local help available.</p>"
        context = {'content': content}
        return render(request, 'local_structure_help.html', context)


# =============================================================================
# SQL helpers
# =============================================================================

def textmatch(column_name: str,
              fragment: str,
              as_fulltext: bool,
              dialect: str = 'mysql') -> str:
    if as_fulltext and dialect == 'mysql':
        return "MATCH({column}) AGAINST ('{fragment}')".format(
            column=column_name, fragment=fragment)
    else:
        return "{column} LIKE '%{fragment}%'".format(
            column=column_name, fragment=fragment)


def sqlhelper_text_anywhere(request: HttpRequest) -> HttpResponse:
    """
    Creates SQL to find text anywhere in the database(s) via a UNION query.
    """
    # When you forget, go back to:
    # http://www.slideshare.net/pydanny/advanced-django-forms-usage
    default_values = {
        'fkname': settings.SECRET_MAP['RID_FIELD'],
        'min_length': 50,
        'use_fulltext_index': True,
        'include_content': False,
    }
    form = SQLHelperTextAnywhereForm(request.POST or default_values)
    grammar = make_grammar(settings.RESEARCH_DB_DIALECT)
    if form.is_valid():
        fkname = form.cleaned_data['fkname']
        min_length = form.cleaned_data['min_length']
        use_fulltext_index = form.cleaned_data['use_fulltext_index']
        include_content = form.cleaned_data['include_content']
        fragment = escape_sql_string_literal(form.cleaned_data['fragment'])
        table_queries = []
        tables = research_database_info.tables_containing_field(fkname)
        if not tables:
            return HttpResponse(
                "No tables containing fieldname: {}".format(fkname))
        if include_content:
            queries = []
            for table_id in tables:
                columns = research_database_info.text_columns(
                    table_id=table_id, min_length=min_length)
                for columninfo in columns:
                    column_identifier = columninfo.column_id().identifier(grammar)  # noqa
                    query = (
                        "SELECT {fkname} AS patient_id,"
                        "\n    '{table_literal}' AS table_name,"
                        "\n    '{col_literal}' AS column_name,"
                        "\n    {column_name} AS content"
                        "\nFROM {table}"
                        "\nWHERE {condition}".format(
                            fkname=fkname,
                            table_literal=escape_sql_string_literal(
                                table_id.identifier(grammar)),
                            col_literal=escape_sql_string_literal(
                                columninfo.column_name),
                            column_name=column_identifier,
                            table=table_id.identifier(grammar),
                            condition=textmatch(
                                column_identifier,
                                fragment,
                                columninfo.indexed_fulltext and use_fulltext_index  # noqa
                            ),
                        )
                    )
                    queries.append(query)
            sql = "\nUNION\n".join(queries)
            sql += "\nORDER BY patient_id".format(fkname)
        else:
            for table_id in tables:
                elements = []
                columns = research_database_info.text_columns(
                    table_id=table_id, min_length=min_length)
                if not columns:
                    continue
                for columninfo in columns:
                    element = textmatch(
                        columninfo.column_id().identifier(grammar),
                        fragment,
                        columninfo.indexed_fulltext and use_fulltext_index)
                    elements.append(element)
                table_query = (
                    "SELECT {fkname} FROM {table} WHERE ("
                    "\n    {elements}\n)".format(
                        fkname=fkname,
                        table=table_id.identifier(grammar),
                        elements="\n    OR ".join(elements),
                    )
                )
                table_queries.append(table_query)
            sql = "\nUNION\n".join(table_queries)
            if sql:
                sql += "\nORDER BY {}".format(fkname)
        if 'submit_save' in request.POST:
            return query_submit(request, sql, run=False)
        elif 'submit_run' in request.POST:
            return query_submit(request, sql, run=True)
        else:
            return render(request, 'sql_fragment.html', {'sql': sql})

    return render(request, 'sqlhelper_form_text_anywhere.html', {'form': form})


# =============================================================================
# Per-patient views
# =============================================================================

def patient_explorer_build(request: HttpRequest) -> HttpResponse:
    profile = request.user.profile
    default_database = get_default_database()
    default_schema = get_default_schema()
    with_database = research_database_info.uses_database_level()
    form = None

    def ensure_pmq() -> None:
        if not profile.patient_multiquery_scratchpad:
            profile.patient_multiquery_scratchpad = PatientMultiQuery()

    if request.method == 'POST':
        if 'global_clear' in request.POST:
            profile.patient_multiquery_scratchpad = PatientMultiQuery()
            profile.save()

        elif 'global_save' in request.POST:
            return pe_submit(
                request, profile.patient_multiquery_scratchpad, run=False)

        elif 'global_run' in request.POST:
            return pe_submit(
                request, profile.patient_multiquery_scratchpad, run=True)

        else:
            form = QueryBuilderForm(request.POST, request.FILES)
            if form.is_valid():
                # log.critical("is_valid")
                database = (form.cleaned_data['database'] if with_database
                            else '')
                schema = form.cleaned_data['schema']
                table = form.cleaned_data['table']
                column = form.cleaned_data['column']
                column_id = ColumnId(db=database, schema=schema,
                                     table=table, column=column)

                if 'submit_select' in request.POST:
                    ensure_pmq()
                    profile.patient_multiquery_scratchpad\
                        .add_output_column(column_id)  # noqa

                elif 'submit_where' in request.POST:
                    datatype = form.cleaned_data['datatype']
                    op = form.cleaned_data['where_op']
                    # Value
                    if op in SQL_OPS_MULTIPLE_VALUES:
                        value = form.file_values_list
                    elif op in SQL_OPS_VALUE_UNNECESSARY:
                        value = None
                    else:
                        value = form.get_cleaned_where_value()
                    # WHERE fragment
                    wherecond = WhereCondition(column_id=column_id,
                                               op=op,
                                               datatype=datatype,
                                               value_or_values=value)
                    ensure_pmq()
                    profile.patient_multiquery_scratchpad\
                        .add_patient_condition(wherecond)

                else:
                    raise ValueError("Bad form command!")
                profile.save()

            else:
                # log.critical("not is_valid")
                pass

    if form is None:
        form = QueryBuilderForm()

    starting_values_dict = {
        'database': form.data.get('database', '') if with_database else '',
        'schema': form.data.get('schema', ''),
        'table': form.data.get('table', ''),
        'column': form.data.get('column', ''),
        'op': form.data.get('where_op', ''),
        'date_value': form.data.get('date_value', ''),
        # Impossible to set file_value programmatically. (See querybuilder.js.)
        'float_value': form.data.get('float_value', ''),
        'int_value': form.data.get('int_value', ''),
        'string_value': form.data.get('string_value', ''),
        'offer_where': bool(profile.sql_scratchpad),  # existing SELECT?
        'form_errors': "<br>".join("{}: {}".format(k, v)
                                   for k, v in form.errors.items()),
        'default_database': default_database,
        'default_schema': default_schema,
        'with_database': with_database,
    }

    grammar = make_grammar(settings.RESEARCH_DB_DIALECT)
    pmq = profile.patient_multiquery_scratchpad
    pmq_output_columns = prettify_sql_html("\n".join(
        [column_id.identifier(grammar)
         for column_id in pmq.get_output_columns()]))
    manual_query = pmq.get_manual_patient_id_query()
    if manual_query:
        pmq_patient_conditions = "<div>Overridden by manual query.</div>"
        pmq_manual_patient_query = prettify_sql_html(
            pmq.get_manual_patient_id_query())
    else:
        pmq_patient_conditions = prettify_sql_html("\nAND ".join([
            wc.sql(grammar)
            for wc in pmq.get_patient_conditions()]))
        pmq_manual_patient_query = "<div><i>None</i></div>"
    pmq_final_patient_query = prettify_sql_html(pmq.patient_id_query())

    context = {
        'nav_on_pe_build': True,
        'pmq_output_columns': pmq_output_columns,
        'pmq_patient_conditions': pmq_patient_conditions,
        'pmq_manual_patient_query': pmq_manual_patient_query,
        'pmq_final_patient_query': pmq_final_patient_query,
        'database_structure': get_db_structure_json(),
        'starting_values': json.dumps(starting_values_dict),
        'sql_dialect': settings.RESEARCH_DB_DIALECT,
        'dialect_mysql': settings.RESEARCH_DB_DIALECT == DIALECT_MYSQL,
        'dialect_mssql': settings.RESEARCH_DB_DIALECT == DIALECT_MSSQL,
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'pe_build.html', context)


def patient_explorer_choose(request: HttpRequest) -> HttpResponse:
    all_pes = get_all_pes(request)
    patient_explorers = paginate(request, all_pes)
    profile = request.user.profile
    element_counter = HtmlElementCounter()
    context = {
        'nav_on_pe_choose': True,
        'patient_explorers': patient_explorers,
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'pe_choose.html', context)


def patient_explorer_activate(request: HttpRequest,
                              pe_id: int) -> HttpResponse:
    validate_blank_form(request)
    pe = get_object_or_404(PatientExplorer, id=pe_id)  # type: PatientExplorer
    pe.activate()
    return redirect('pe_choose')


def patient_explorer_delete(request: HttpRequest, pe_id: int) -> HttpResponse:
    validate_blank_form(request)
    pe = get_object_or_404(PatientExplorer, id=pe_id)  # type: PatientExplorer
    pe.delete_if_permitted()
    return redirect('pe_choose')


def patient_explorer_results(request: HttpRequest, pe_id: int) -> HttpResponse:
    pe = get_object_or_404(PatientExplorer, id=pe_id)  # type: PatientExplorer
    grammar = make_grammar(settings.RESEARCH_DB_DIALECT)
    profile = request.user.profile
    highlights = Highlight.get_active_highlights(request)
    highlight_dict = Highlight.as_ordered_dict(highlights)
    element_counter = HtmlElementCounter()
    patient_id_query_html = prettify_sql_html(pe.get_patient_id_query())
    try:
        trids = pe.get_patient_trids()
        page = paginate(request, trids,
                        per_page=get_patients_per_page(request))
        active_trids = list(page)
        results = []
        for table_id, sql in pe.all_queries(trids=active_trids):
            with pe.get_executed_cursor(sql) as cursor:
                fieldnames = get_fieldnames_from_cursor(cursor)
                rows = cursor.fetchall()
                table_html = resultset_html_table(
                    fieldnames=fieldnames,
                    rows=rows,
                    element_counter=element_counter,
                    highlight_dict=highlight_dict,
                    collapse_at_len=profile.collapse_at_len,
                    collapse_at_n_lines=profile.collapse_at_n_lines,
                    line_length=profile.line_length,
                )
                query_html = element_counter.collapsible_div_with_divbutton(
                    contents=prettify_sql_html(sql),
                    title_html="SQL")
                results.append({
                    'tablename': table_id.identifier(grammar),
                    'table_html': table_html,
                    'query_html': query_html,
                })
        context = {
            'nav_on_pe_results': True,
            'results': results,
            'page': page,
            'rowcount': len(trids),
            'patient_id_query_html': patient_id_query_html,
            'sql_highlight_css': prettify_sql_css(),
        }
        context.update(query_context(request))
        return render(request, 'pe_result.html', context)

    except DatabaseError as exception:
        return render_bad_pe(request, pe, exception)


def render_missing_pe(request: HttpRequest) -> HttpResponse:
    return render(request, 'pe_missing.html', query_context(request))


def render_bad_pe(request: HttpRequest,
                  pe: PatientExplorer,
                  exception: Exception) -> HttpResponse:
    context = {
        'queries': [prettify_sql_html(sql) for _, sql in pe.all_queries()],
        'exception': str(exception),
        'sql_highlight_css': prettify_sql_css(),
    }
    context.update(query_context(request))
    return render(request, 'pe_bad.html', context)


# def render_bad_pe_id(request: HttpRequest, pe_id: int) -> HttpResponse:
#     context = {'pe_id': pe_id}
#     context.update(query_context(request))
#     return render(request, 'pe_bad_id.html', context)


def get_all_pes(request: HttpRequest) -> QuerySet:
    return PatientExplorer.objects\
        .filter(user=request.user, deleted=False)\
        .order_by('-active', '-created')


def pe_submit(request: HttpRequest,
              pmq: PatientMultiQuery,
              run: bool = False) -> HttpResponse:
    all_pes = get_all_pes(request)
    identical_pes = all_pes.filter(patient_multiquery=pmq) # *** Check: does this work?
    if identical_pes:
        identical_pes[0].activate()
        pe_id = identical_pes[0].id
    else:
        pe = PatientExplorer(patient_multiquery=pmq,
                             user=request.user,
                             active=True)
        pe.save()
        pe_id = pe.id
    # redirect to a new URL:
    if run:
        return redirect('pe_results', pe_id)
    else:
        return redirect('pe_choose')


def patient_explorer_tsv_zip(request: HttpRequest, pe_id: int) -> HttpResponse:
    # http://stackoverflow.com/questions/12881294/django-create-a-zip-of-multiple-files-and-make-it-downloadable  # noqa
    pe = get_object_or_404(PatientExplorer, id=pe_id)  # type: PatientExplorer
    try:
        zipdata = pe.get_zipped_tsv_binary_data()
        resp = HttpResponse(zipdata, content_type=CONTENTTYPE_ZIP)
        filename = "crate_pe_{num}_{datetime}.zip".format(
            num=pe.id,
            datetime=datetime_iso_for_filename(),
        )
        resp['Content-Disposition'] = "attachment;filename={}".format(filename)
        return resp
    except DatabaseError as exception:
        return render_bad_pe(request, pe, exception)


def patient_explorer_excel(request: HttpRequest, pe_id: int) -> HttpResponse:
    pe = get_object_or_404(PatientExplorer, id=pe_id)  # type: PatientExplorer
    try:
        xlsxdata = pe.get_xlsx_binary_data()
        resp = HttpResponse(xlsxdata, content_type=CONTENTTYPE_XLSX)
        filename = "crate_patientexplorer_{num}_{datetime}.xlsx".format(
            num=pe.id,
            datetime=datetime_iso_for_filename(),
        )
        resp['Content-Disposition'] = "attachment;filename={}".format(filename)
        return resp
    except DatabaseError as exception:
        return render_bad_pe(request, pe, exception)
