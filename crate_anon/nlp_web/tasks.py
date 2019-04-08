#!/usr/bin/env python

r"""
crate_anon/nlp_web/tasks.py

===============================================================================

    Copyright (C) 2015-2019 Rudolf Cardinal (rudolf@pobox.com).

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

from celery import Celery
import requests
import transaction
import logging
import datetime
import json
# import time

from cryptography.fernet import Fernet
from sqlalchemy import engine_from_config
from typing import Optional, Tuple, Any, List, Dict

from crate_anon.nlp_manager.base_nlp_parser import BaseNlpParser
# from crate_anon.nlp_manager.all_processors import make_processor
from crate_anon.nlp_web.models import DBSession, DocProcRequest
from crate_anon.nlp_web.procs import Processor
from crate_anon.nlp_web.constants import PROCTYPE_GATE, SETTINGS
from crate_anon.nlp_web.security import decrypt_password

log = logging.getLogger(__name__)

try:
    broker_url = SETTINGS['broker_url']
except KeyError:
    log.error("broker_url value missing from config file.")
    raise
try:
    backend_url = SETTINGS['backend_url']
except KeyError:
    log.error("backend_url value missing from config file.")
    raise

key = SETTINGS['encryption_key']
# Turn key into bytes object
key = key.encode()
CIPHER_SUITE = Fernet(key)


def get_gate_results(results_dict: Dict[str, Any]) -> List[Any]:
    results = []
    # See https://cloud.gate.ac.uk/info/help/online-api.html
    # for format of response from processor
    text = results_dict['text']
    entities = results_dict['entities']
    for annottype, values in entities.items():
        # One annotation type will have a list of dictionaries
        # with each dictionary being the set of features for one
        # result, or 'hit'
        for featureset in values:
            # There must be a more efficient way to do this:
            features = {x: featureset[x] for x in featureset if x != "indices"}
            features['_type'] = annottype
            start, end = featureset['indices']
            content = text[start: end]
            features['_start'] = start
            features['_end'] = end
            features['_content'] = content
            results.append(features)
    return results


app = Celery('tasks', backend=backend_url, broker=broker_url)

log = logging.getLogger(__name__)


# noinspection PyUnusedLocal
@app.task(bind=True, name='tasks.process_nlp_text')
def process_nlp_text(
        self,
        docprocrequest_id: str,
        url: str = None,
        username: str = "",
        crypt_pass: str = "") -> Optional[Tuple[bool, List[Any], Optional[int],
                                                str, datetime.datetime]]:
    """
    Task to send text to the relevant processor.
    """
    # time.sleep(5)
    # Can't figure out how not to have to do this everytime
    engine = engine_from_config(SETTINGS, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    query = DBSession.query(DocProcRequest).get(docprocrequest_id)
    # The above is probably wrong, but if we use a different session, the
    # data doesn't always reach the database in time
    if not query:
        log.error("Docprocrequest: {} does not exist: ".format(
                      docprocrequest_id))
        return None
    # Turn the password back into bytes and decrypt
    password = decrypt_password(crypt_pass.encode(), CIPHER_SUITE)
    text = query.doctext
    processor_id = query.processor_id
    processor = Processor.processors[processor_id]
    # Delete docprocrequest from database
    DBSession.delete(query)
    transaction.commit()
    if processor.proctype == PROCTYPE_GATE:
        return process_nlp_gate(text, processor, url, username, password)
    else:
        if not processor.parser:
            processor.set_parser()
        return process_nlp_internal(text=text, parser=processor.parser)


def process_nlp_text_immediate(
        text: str,
        processor: Processor,
        url: str = None,
        username: str = "",
        password: str = "") -> Optional[Tuple[bool, List[Any], Optional[int],
                                              str, datetime.datetime]]:
    """
    Function to send text immediately to the relevant processor.
    """
    if processor.proctype == PROCTYPE_GATE:
        return process_nlp_gate(text, processor, url, username, password)
    else:
        if not processor.parser:
            processor.set_parser()
        return process_nlp_internal(text=text, parser=processor.parser)


def process_nlp_gate(text: str, processor: Processor, url: str,
                     username: str, password: str) -> Tuple[
            bool, List[Any], Optional[int], Optional[str], datetime.datetime]:
    """
    Send text to a chosen GATE processor and returns a Tuple in the format
    (sucess, results, error code, error message) where success is True or
    False, results is None if sucess is False and error code and error message
    are None if success is True.
    """
    headers = {
        'Content-Type': 'text/plain',
        'Accept': 'application/gate+json',
        # Content-Encoding: gzip?,
        'Expect': '100-continue',   # see https://cloud.gate.ac.uk/info/help/online-api.html  # noqa
        'charset': 'utf8'
    }
    text = text.encode('utf-8')
    try:
        response = requests.post(url + '/' + processor.name,
                                 data=text,
                                 headers=headers,
                                 auth=(username, password))  # basic auth
        print(response)
    except requests.exceptions.RequestException as e:
        log.error(e)
        return (
            False,
            [],
            e.response.status_code,
            "The GATE processor returned the error: " + e.response.reason,
            datetime.datetime.utcnow()
        )
    if response.status_code != 200:
        return (
            False,
            [],
            response.status_code,
            "The GATE processor returned the error: " + response.reason,
            datetime.datetime.utcnow()
        )
    try:
        json_response = response.json()
    except json.decoder.JSONDecodeError:
        return (
            False,
            [],
            502,  # 'Bad Gateway' - not sure if correct error code
            "The GATE processor did not return json",
            datetime.datetime.utcnow()
        )
    results = get_gate_results(json_response)
    print(results)
    return True, results, None, None, datetime.datetime.utcnow()


def process_nlp_internal(text: str, parser: BaseNlpParser) -> Tuple[
            bool, List[Any], Optional[int], Optional[str], datetime.datetime]:
    """
    Send text to a chosen Python processor and returns a Tuple in the format
    (sucess, results, error code, error message) where success is True or
    False, results is None if sucess is False and error code and error message
    are None if success is True.
    """
    # processor = make_processor(processor_type=processor,
    #                            nlpdef=None, cfgsection=None)
    try:
        parsed_text = parser.parse(text)
    except AttributeError:
        # 'parser' is not actual parser - must have happened internally
        return (
            False,
            [],
            500,  # 'Internal Server Error'
            "Internal Server Error",
            datetime.datetime.utcnow()
        )
    # Get second element of each element in parsed text as first is tablename
    # which will have no meaning here
    return (
        True,
        [x[1] for x in parsed_text],
        None,
        None,
        datetime.datetime.utcnow()
    )
