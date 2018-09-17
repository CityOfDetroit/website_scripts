#!/usr/bin/env python

import json


def get_secrets():

    with open("../django_apps/secrets.json") as input:

        secrets = input.read()
        return json.loads(secrets)
