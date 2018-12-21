#!/usr/bin/env python

from sshtunnel import SSHTunnelForwarder, create_logger
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from util import get_secrets

from parse_translated_content import TranslatedPage


class TranslationsLoader():

    def __init__(self, dbname):

        self.dbname = dbname
        self.db_info = get_secrets()["DATABASES"][self.dbname]
        self.ssh_host = self.db_info["SSH_HOST"]
        self.db_name = self.db_info["NAME"]
        self.db_engine = self.db_info["ENGINE"]
        self.db_user = self.db_info["USER"]
        self.db_pass = self.db_info["PASSWORD"]

    def start(self):
        """
        Connect to server (ssh as well as database).
        """

        self.server = SSHTunnelForwarder(
                ssh_address_or_host=self.ssh_host,
                ssh_username=self.dbname,
                ssh_pkey='~/.ssh/id_rsa',
                remote_bind_address=('127.0.0.1', 3306),
                    logger=create_logger(loglevel=0))

        self.server.start()

        local_port=str(self.server.local_bind_port)

        self.engine = create_engine('{}://{}:{}@127.0.0.1:{}/{}?charset=utf8mb4'.format(self.db_engine, self.db_user, self.db_pass, local_port, self.db_name))
        self.conn = self.engine.connect()

    def table_names(self):

        tables = self.engine.table_names()
        for table in tables:
            print(table)

    def load_page(self, page, lang):
        """
        Load a page of translated content.
        """


        # description (all taxonomies):
        # select description__value from taxonomy_term_field_data where tid = 1141;

        # summary (departments only):
        # taxonomy_term__field_summary -> field_summary_value
        # select * from taxonomy_term__field_summary where bundle = 'departments' and langcode = 'en' and entity_id = 1411;

        sql = text(
            "update taxonomy_term_field_data tfd "
            "set tfd.name = :name, tfd.description__value = :desc "
            "where tfd.langcode = :lang and tfd.tid = :tid;")

        self.engine.execute(sql, name=page.title, desc=page.desc, lang=lang, tid=page.tid)

        # Now update summary (departments only):
        if page.vid == 'departments':

            sql = text(
                "update taxonomy_term__field_summary tfs "
                "set tfs.field_summary_value = :summary "
                "where tfs.bundle = 'departments' and tfs.langcode = :lang and tfs.entity_id = :tid and tfs.revision_id = :tid;")

            self.engine.execute(sql, summary=page.summary, lang=lang, tid=page.tid)

        elif page.vid == 'government':

            sql = text(
                "update taxonomy_term__field_organization_head_informat tfo "
                "set tfo.field_organization_head_informat_value = :informat "
                "where tfo.bundle = 'government' and tfo.langcode = :lang and tfo.entity_id = :tid and tfo.revision_id = :tid;")

            self.engine.execute(sql, informat=page.organization_head_information, lang=lang, tid=page.tid)

        # field_organization_head_informat_value (government):
        # select * from taxonomy_term__field_organization_head_informat where bundle = 'government' and langcode = 'en' and entity_id = 1276;


    def check_page(self, page, lang):
        """
        Verify that the given page got updated correctly.
        """

        sql = text(
            "select tfd.tid, tfd.name, tfd.description__value "
            "from taxonomy_term_field_data tfd "
            "where tfd.langcode = :lang and tfd.tid = :tid "
            "order by tfd.name;")

        results = self.conn.execute(sql, lang=lang, tid=page.tid).fetchall()

        if len(results) != 1:
            raise Exception('Wrong # of rows returned checking page name and description')

        for row in results:
            if row['name'] != page.title:
                raise Exception('Page name did not update properly')
            if row['description__value'] != page.desc:
                raise Exception('Page description did not update properly')

        if page.vid == 'departments':

            sql = text(
                "select tfs.field_summary_value "
                "from taxonomy_term__field_summary tfs "
                "where tfs.bundle = 'departments' and tfs.langcode = :lang and tfs.entity_id = :tid;")

            results = self.conn.execute(sql, lang=lang, tid=page.tid).fetchall()

            if len(results) != 1:
                raise Exception('Wrong # of rows returned checking department summary')

            for row in results:
                if row['field_summary_value'] != page.summary:
                    raise Exception('Page summary did not update properly')

        elif page.vid == 'government':

            sql = text(
                "select tfo.field_organization_head_informat_value "
                "from taxonomy_term__field_organization_head_informat tfo "
                "where tfo.bundle = 'government' and tfo.langcode = :lang and tfo.entity_id = :tid and tfo.revision_id = :tid;")

            results = self.conn.execute(sql, lang=lang, tid=page.tid).fetchall()

            if len(results) > 1:
                raise Exception('Wrong # of rows returned checking government org head info')

            for row in results:
                if row['field_organization_head_informat_value'] != page.organization_head_information:
                    raise Exception('Page org head info did not update properly')



    def stop(self):
        """
        Disconnect and stop server and database connections.
        """

        self.conn.close()
        self.engine.dispose()

        self.server.stop()
