#!/usr/bin/env python

import os
import requests
import shutil


SAMPLE_BALLOT = "./sample_ballot.pdf"
FILE_SYSTEM_TREE = "./election_info/precincts/"
URL = "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Elections_2019/FeatureServer/0/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=json"


if __name__ == '__main__':

    response = requests.get(URL)

    data = response.json()

    precincts = [ attribute['attributes']['precinct'] for attribute in data['features'] if attribute.get('attributes', {}).get('precinct') ]
    precincts = sorted(precincts)

    for precinct in precincts:

        dest_dir = FILE_SYSTEM_TREE + str(precinct) + "/"

        os.mkdir(dest_dir)
        location = shutil.copy(SAMPLE_BALLOT, dest_dir)
        print(location)
