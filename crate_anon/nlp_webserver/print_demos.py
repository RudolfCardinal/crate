#!/usr/bin/env python

r"""
crate_anon/nlp_webserver/print_demo_config.py

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

Prints a demo config for CRATE's implementation of an NLPRP server.
"""

import argparse
import logging

from cardinal_pythonlib.logs import main_only_quicksetup_rootlogger

from crate_anon.nlp_webserver.constants import NlpServerConfigKeys

log = logging.getLogger(__name__)


def demo_config() -> str:
    """
    Returns a demo config ``.ini`` for the CRATE NLPRP web server.
    """
    k = NlpServerConfigKeys
    return (f"""
[app:main]
use = egg:crate_anon#main
pyramid.reload_templates = true
# pyramid.includes =
#     pyramid_debugtoolbar

{k.NLP_WEBSERVER_SECRET} = changethis
{k.SQLALCHEMY_URL_FULL} = mysql://username:password@localhost/dbname?charset=utf8

# Absolute path of users file
{k.USERS_FILE} = /home/.../nlp_web_files/users.txt

# Absolute path of processors file - this must be a .py file in the correct
# format
{k.PROCESSORS_PATH} = /home/.../nlp_web_files/processor_constants.py

# URLs for queueing
{k.BROKER_URL} = amqp://@localhost:3306/testbroker
{k.BACKEND_URL} = db+mysql://username:password@localhost/backenddbname?charset=utf8

# Key for reversible encryption. Use 'nlp_webserver_generate_encryption_key'.
{k.ENCRYPTION_KEY} =

[server:main]
use = egg:waitress#main
listen = localhost:6543
"""  # noqa
    )


def demo_processors() -> str:
    """
    Returns a demo ``processors.py`` for the CRATE NLPRP web server, which
    the user can then configure.
    """
    return ('''#!/usr/bin/env python

"""
Autogenerated NLP processor definition file, to be imported by the CRATE
NLPRP web server. The PROCESSORS variable is the one of interest.
"""

# =============================================================================
# Imports
# =============================================================================

from crate_anon.nlp_manager.all_processors import (
    all_crate_python_processors_nlprp_processor_info
)
from crate_anon.nlprp.constants import NlprpValues, NlprpKeys as NKeys
from crate_anon.nlp_webserver.constants import (
    KEY_PROCTYPE,
    PROCTYPE_GATE,
)


# =============================================================================
# Processor definitions
# =============================================================================

# GATE processors correct as of 19/04/2019 for KCL server.
# Python processors are automatic, as below.

PROCESSORS = [
    # -------------------------------------------------------------------------
    # GATE processors
    # -------------------------------------------------------------------------
    {
        NKeys.NAME: "medication",
        NKeys.TITLE: "GATE processor: Medication tagger",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of drug prescriptions, "
                           "including the dose, route and frequency.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "diagnosis",
        NKeys.TITLE: "GATE processor: Diagnosis finder",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of diagnoses, in words or "
                           "in coded form.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "blood-pressure",
        NKeys.TITLE: "GATE processor: Blood Pressure",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of blood pressure measurements.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "cbt",
        NKeys.TITLE: "GATE processor: Cognitive Behavioural Therapy",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Identifies mentions of cases where the patient "
                           "has attended CBT sessions.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "lives-alone",
        NKeys.TITLE: "GATE processor: Lives Alone",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Identifies if the patient lives alone.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "mmse",
        NKeys.TITLE: "GATE processor: Mini-Mental State Exam Result Extractor",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "The Mini-Mental State Exam (MMSE) Results "
                           "Extractor finds the results of this common "
                           "dementia screening test within documents along "
                           "with the date on which the test was administered.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "bmi",
        NKeys.TITLE: "GATE processor: Body Mass Index",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds mentions of BMI scores.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "smoking",
        NKeys.TITLE: "GATE processor: Smoking Status Annotator",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Identifies instances of smoking being discussed "
                           "and determines the status and subject (patient or "
                           "someone else).",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "ADR",
        NKeys.TITLE: "GATE processor: ADR",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Adverse drug event mentions in clinical notes.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "suicide",
        NKeys.TITLE: "GATE processor: Symptom finder - Suicide",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "App derived from TextHunter project suicide.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "appetite",
        NKeys.TITLE: "GATE processor: Symptom finder - Appetite",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "Finds markers of good or poor appetite.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
    {
        NKeys.NAME: "low_mood",
        NKeys.TITLE: "GATE processor: Symptom finder - Low_Mood",
        NKeys.VERSION: "0.1",
        NKeys.IS_DEFAULT_VERSION: True,
        NKeys.DESCRIPTION: "App derived from TextHunter project low_mood.",
        KEY_PROCTYPE: PROCTYPE_GATE,
        NKeys.SCHEMA_TYPE: NlprpValues.UNKNOWN
    },
] + all_crate_python_processors_nlprp_processor_info()


# =============================================================================
# Convenience method: if you run the file, it prints its results.
# =============================================================================

if __name__ == "__main__":
    import json  # delayed import
    print(json.dumps(PROCESSORS, indent=4, sort_keys=True))
'''  # noqa
    )


def main() -> None:
    """
    Command line entry point.
    """
    description = ("Print demo config file or demo processor constants file "
                   "for server side cloud nlp.")
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    arg_group = parser.add_mutually_exclusive_group()
    arg_group.add_argument(
        "--config", action="store_true",
        help="Print a demo config file for server side cloud nlp.")
    arg_group.add_argument(
        "--processors", action="store_true",
        help="Print a demo processor constants file for server side cloud "
             "nlp.")
    args = parser.parse_args()

    main_only_quicksetup_rootlogger()

    if args.config:
        print(demo_config())
    elif args.processors:
        print(demo_processors())
    else:
        log.error("One option required: '--config' or '--processors'.")
