#!/usr/bin/env python

r"""
crate_anon/nlp_webserver/initialize_db.py

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

Tool to initialize the database used by CRATE's implementation of an NLPRP
server.

"""

import argparse

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings

from crate_anon.nlp_webserver.constants import NlpServerConfigKeys
from crate_anon.nlp_webserver.models import DBSession, Base


def main() -> None:
    """
    Command-line entry point.
    """
    parser = argparse.ArgumentParser(
        description="Tool to initialize the database used by CRATE's "
                    "implementation of an NLPRP server."
    )
    parser.add_argument(
        "config_uri", type=str,
        help="Config file to read (e.g. 'development.ini'); URL of database "
             "is found here."
    )
    args = parser.parse_args()

    settings = get_appsettings(args.config_uri)
    engine = engine_from_config(settings,
                                NlpServerConfigKeys.SQLALCHEMY_URL_PREFIX)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()