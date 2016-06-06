#!/usr/bin/python3

import requests
import json
import os


def get_json(url):
    username = 'admin'
    password = 'benedict'
    r = requests.get(url, auth=(username, password))
    return r.json()


if not os.path.exists("build-info"):
    os.makedirs("build-info")

mf = open("manifest.txt", "w")

with open("projectList.txt") as f:
    projNames = f.readlines()

for projName in projNames:
    projName = projName.strip('\n')
    data = get_json('http://localhost:8081/artifactory/api/build/%s' % projName)
    maxBuildNo = data['buildsNumbers'][0]['uri'][1:]
    for obj in data['buildsNumbers']:
        if obj['uri'][1:] > maxBuildNo:
            maxBuildNo = obj['uri'][1:]

    data = get_json('http://localhost:8081/artifactory/api/build/%s/%s' % (projName, maxBuildNo))
    version_no = data["buildInfo"]["properties"]["buildInfo.env.VERSION_NUMBER"].strip()
    commit_id = data["buildInfo"]["properties"]["buildInfo.env.GIT_COMMIT"]
    mf.write("%s:\nVERSION NUMBER: %s\nGIT COMMIT ID: %s\n" % (projName, version_no, commit_id))

    fd = open("build-info/%s_%s.json" % (projName, version_no), "w")
    json.dump(data, fd)
    fd.close()

mf.close()
