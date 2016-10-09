﻿#!/usr/bin/env python
import os
import re
import sys
import collections
import functools
import yaml

from python.pl import swift

Entry = collections.namedtuple("Entry","inputFolders, outputPath, prefix, enum")

def createEntry(prefix , output, enum, *inputdata):
    return Entry(inputdata, output, prefix, enum)

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)',r'\1_\2',name)
    return re.sub("([a-x0-9])([A-Z])",r"\1_\2",s1).lower()

def iOSBaseName(fileName):
    fileName = fileName.replace(".plist","")
    fileName = fileName.replace("@","~")
    names    = fileName.split("~")
    return names[0]

def preprocessorFormat(name, prefix = "PLIST_"):
    name = convert(name).upper()
    name = name.replace(" ","_")
    currentLength = len(name)
    while True:
        name =  name.replace("__","_")
        newLength = len(name)
        if currentLength == newLength:
            break
        currentLength = newLength
    return prefix+name

def processEntry(entry):
    fileNames = []
    for folder in entry.inputFolders :
        for currentDirectory , subDirectories, files  in os.walk(os.path.abspath(folder)):
            map(fileNames.append , files)

    uniqueFileNames= list(set(map(iOSBaseName, fileNames)))
    uniqueFileNames.sort()
    if ".DS_Store" in uniqueFileNames:
        uniqueFileNames.remove(".DS_Store")
    formatter= functools.partial(preprocessorFormat, prefix = entry.prefix)
    preprocessorNames = map(formatter,uniqueFileNames)

    with open(entry.outputPath, "w", encoding="UTF-8") as writer:
        s = swift.Swift(writer)
        values = zip(preprocessorNames, uniqueFileNames)
        s.enumeration(entry.enum, values, "String")

if __name__ == '__main__':
    try:
        yamlPath = sys.argv[1]
    except:
        yamlPath = "./config.yaml"

    with open(yamlPath, 'r', encoding='UTF-8') as reader:
        data = yaml.load(reader)
        plistData = data["plists"]

        for plist in plistData:
            entry = createEntry(plist["prefix"], plist["output"], plist["enum"], plist["folder"])
            processEntry(entry)