#!/usr/bin/env python

from sshtunnel import SSHTunnelForwarder, create_logger
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from util import get_secrets

from parse_translated_content import TranslatedPage


import pdb


class TranslationsLoader():

    db_info = get_secrets()["DATABASES"]["detroitmi.dev"]
    ssh_host = db_info["SSH_HOST"]
    db_name = db_info["NAME"]
    db_engine = db_info["ENGINE"]
    db_user = db_info["USER"]
    db_pass = db_info["PASSWORD"]

    def start(self):
        """
        Connect to server (ssh as well as database).
        """

        self.server = SSHTunnelForwarder(
                ssh_address_or_host=self.ssh_host,
                ssh_username='detroitmi.dev',
                ssh_pkey='~/.ssh/id_rsa',
                remote_bind_address=('127.0.0.1', 3306),
                logger=create_logger(loglevel=0))

        self.server.start()

        local_port=str(self.server.local_bind_port)

        self.engine = create_engine('{}://{}:{}@127.0.0.1:{}/{}'.format(self.db_engine, self.db_user, self.db_pass, local_port, self.db_name))
        self.conn = self.engine.connect()

    def load_page(self, page, lang):
        """
        Load a page of translated content.
        """


        pdb.set_trace()


        sql = text(" \
            update taxonomy_term_field_data_delme tfd \
            inner join taxonomy_term_hierarchy_delme tth \
            on tth.tid = tfd.tid \
            set tfd.name = {} \
            where tfd.langcode = '{}' and tth.tid = {}; \
            ".format(page.title, lang, page.tid))

        self.engine.execute(sql)


        sql = text(" \
            select tth.tid, tfd.name \
            from taxonomy_term_hierarchy_delme tth \
            join taxonomy_term_field_data_delme tfd \
            on tth.tid = tfd.tid \
            where tfd.langcode = '{}' and tth.tid = {} \
            order by tfd.name; \
            ".format(lang, page.tid))

        results = self.conn.execute(sql).fetchall()

        for row in results:
        	print(row)

    def stop(self):
        """
        Disconnect and stop server and database connections.
        """

        self.conn.close()
        self.engine.dispose()

        self.server.stop()
