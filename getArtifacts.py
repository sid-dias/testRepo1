#!/usr/bin/python3
import glob
import json
import re
import requests
import os
import sys

username = 'admin'
password = 'benedict'


def get_artifact(repo, projName, version_no, fileName):
    url = 'http://172.17.0.1:8081/artifactory/%s/%s/%s/%s' % (repo, projName, version_no, fileName)
    r = requests.get(url, auth=(username, password))
    if not os.path.exists("artifacts/"+projName):
        os.makedirs("artifacts/"+projName)
    file = open("artifacts/%s/%s" % (projName, fileName), "wb")
    file.write(r.content)


version = sys.argv[1]
url = 'http://172.17.0.1:8081/artifactory/versionInfo/%s/' % version
r = requests.get(url, auth=(username, password))

listFile = str(r.content, encoding="utf-8")
fileNames = re.findall(r'\n<a href=\"([^"]*)\"', listFile)
fileNames = list(filter(lambda x: not (x.endswith("md5") or x.endswith("sha1")), fileNames))

if not os.path.exists("build-info"):
    os.makedirs("build-info")

for file in fileNames:
    url = 'http://172.17.0.1:8081/artifactory/versionInfo/%s/%s' % (version, file)
    r = requests.get(url, auth=(username, password))
    fd = open("build-info/%s" % file, "wb")
    fd.write(r.content)
    fd.close()

if not os.path.exists("artifacts"):
    os.makedirs("artifacts")

for fileName in glob.glob("./build-info/*.json"):
    fd = open(fileName)
    jdata = json.load(fd)

    projName = re.search(r'/([a-zA-Z0-9]+)_', fileName).group(1)
    repo = jdata["buildInfo"]["properties"]["buildInfo.env.REPOSITORY"]
    version_no = jdata["buildInfo"]["properties"]["buildInfo.env.VERSION_NUMBER"]

    for artifact in jdata["buildInfo"]["modules"][0]["artifacts"]:
        get_artifact(repo, projName, version_no, artifact["name"])

    print("Done fetching artifacts of " + projName)
