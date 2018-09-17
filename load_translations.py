#!/usr/bin/env python

from sshtunnel import SSHTunnelForwarder, create_logger
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from util import get_secrets


db_info = get_secrets()["DATABASES"]["detroitmi.dev"]
ssh_host = db_info["SSH_HOST"]
db_name = db_info["NAME"]
db_engine = db_info["ENGINE"]
db_user = db_info["USER"]
db_pass = db_info["PASSWORD"]


server = SSHTunnelForwarder(
        ssh_address_or_host=ssh_host,
        ssh_username='detroitmi.dev',
        ssh_pkey='~/.ssh/id_rsa',
        remote_bind_address=('127.0.0.1', 3306),
        logger=create_logger(loglevel=0))

server.start()

local_port=str(server.local_bind_port)


engine = create_engine('{}://{}:{}@127.0.0.1:{}/{}'.format(db_engine, db_user, db_pass, local_port, db_name))
conn = engine.connect()

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

results = conn.execute(sql).fetchall()

for row in results:
	print(row)

conn.close()
engine.dispose()

server.stop()
