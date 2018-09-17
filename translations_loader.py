#!/usr/bin/env python

from sshtunnel import SSHTunnelForwarder, create_logger
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from util import get_secrets

from parse_translated_content import TranslatedPage


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



        # Update page title and description (all taxonomies)
        sql = text(" \
            update taxonomy_term_field_data tfd \
            set tfd.name = '{}', tfd.description__value = '{}' \
            where tfd.langcode = '{}' and tfd.tid = {}; \
            ".format(page.title, page.desc, lang, page.tid))

        self.engine.execute(sql)

        # Now update summary (departments only):
        if page.vid == 'departments':

            sql = text(" \
                update taxonomy_term__field_summary tfs \
                set tfs.field_summary_value = '{}' \
                where tfs.bundle = 'departments' and tfs.langcode = '{}' and tfs.entity_id = {} and tfs.revision_id = {}; \
                ".format(page.summary, lang, page.tid, page.tid))

            self.engine.execute(sql)

        elif page.vid == 'government':

            sql = text(" \
                update taxonomy_term__field_organization_head_informat tfo \
                set tfo.field_organization_head_informat_value = '{}' \
                where tfo.bundle = 'government' and tfo.langcode = '{}' and tfo.entity_id = {} and tfo.revision_id = {}; \
                ".format(page.organization_head_information, lang, page.tid, page.tid))

            self.engine.execute(sql)

        # field_organization_head_informat_value (government):
        # select * from taxonomy_term__field_organization_head_informat where bundle = 'government' and langcode = 'en' and entity_id = 1276;


    def check_page(self, page, lang):
        """
        Verify that the given page got updated correctly.
        """

        sql = text(" \
            select tfd.tid, tfd.name, tfd.description__value \
            from taxonomy_term_field_data tfd \
            where tfd.langcode = '{}' and tfd.tid = {} \
            order by tfd.name; \
            ".format(lang, page.tid))

        results = self.conn.execute(sql).fetchall()

        if len(results) != 1:
            raise exception('Wrong # of rows returned checking page name and description')

        for row in results:
            if row['name'] != page.title:
                raise exception('Page name did not update properly')
            if row['description__value'] != page.desc:
                raise exception('Page description did not update properly')

        if page.vid == 'departments':

            sql = text(" \
                select tfs.field_summary_value \
                from taxonomy_term__field_summary tfs \
                where tfs.bundle = 'departments' and tfs.langcode = '{}' and tfs.entity_id = {}; \
                ".format(lang, page.tid))

            results = self.conn.execute(sql).fetchall()

            if len(results) != 1:
                raise exception('Wrong # of rows returned checking department summary')

            for row in results:
                if row['field_summary_value'] != page.summary:
                    raise exception('Page summary did not update properly')

        elif page.vid == 'government':

            sql = text(" \
                select tfo.field_organization_head_informat_value \
                from taxonomy_term__field_organization_head_informat tfo \
                where tfo.bundle = 'government' and tfo.langcode = '{}' and tfo.entity_id = {} and tfo.revision_id = {}; \
                ".format(lang, page.tid, page.tid))

            self.engine.execute(sql)

            if len(results) != 1:
                raise exception('Wrong # of rows returned checking government org head info')

            for row in results:
                if row['field_organization_head_informat_value'] != page.organization_head_information:
                    raise exception('Page org head info did not update properly')



    def stop(self):
        """
        Disconnect and stop server and database connections.
        """

        self.conn.close()
        self.engine.dispose()

        self.server.stop()
