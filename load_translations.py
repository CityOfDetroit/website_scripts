#!/usr/bin/env python

from sshtunnel import SSHTunnelForwarder, create_logger
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from util import get_secrets


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

    def test(self):
        """
        Do sql stuff.
        """

        # tables = engine.table_names()
        # print("num tables:  {}".format(len(tables)))

        sql = text(" \
            select tth.tid, tfd.name \
            from taxonomy_term_hierarchy tth \
            join taxonomy_term_field_data tfd \
            on tth.tid = tfd.tid \
            where tfd.langcode = 'en' \
            order by tfd.name; \
            ")

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

if __name__ == '__main__':

    loader = TranslationsLoader()

    loader.start()
    loader.test()
    loader.stop()
