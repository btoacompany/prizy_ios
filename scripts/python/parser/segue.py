import os
import xml.etree.ElementTree as ET
import pprint
import re
import collections
import sys
from os.path import dirname
parent = os.path.join(dirname(__file__),"../..")
absParent = os.path.abspath(parent)
sys.path.append(absParent)

import yaml

from python.pl import swift
Entry = collections.namedtuple("Entry","inputFolders, outputPath, prefix, enum")

def createEntry(prefix , output, enum, *inputdata):
    return Entry(inputdata, output, prefix, enum)

def getSegueFromStoryboard(storyboardPath,segueList):
    tree = ET.parse(storyboardPath)
    root = tree.getroot()

    for child in root.findall('.//segue'):
        if "identifier" not in child.attrib:
            continue
        identifier = child.attrib["identifier"]
        if len(identifier) > 0:
            segueList.append(identifier)
    return segueList

def iOSBaseName(fileName):
    fileName = fileName.replace("@","~")
    names    = fileName.split("~")
    return names[0]

def preprocessorFormat(name, prefix = "PLIST_"):
    names = re.findall('[A-Z][^A-Z]*', name)
    name = "_to_".join(names)
    name = name.upper()
    name = name.replace(" ","_")
    currentLength = len(name)
    while True:
        name =  name.replace("__","_")
        newLength = len(name)
        if currentLength == newLength:
            break
        currentLength = newLength
    return prefix + name

def processEntry(entry):
    segueNames = []

    for folder in entry.inputFolders :
        print(folder)
        for currentDirectory , subDirectories, files  in os.walk(folder):
            for f in files:
                if f.endswith(".storyboard"):
                    print(f)
                    segueNames = getSegueFromStoryboard(os.path.join(currentDirectory,f),segueNames)

    uniqueFileNames= list(set(map(iOSBaseName, segueNames)))
    uniqueFileNames.sort()
    preprocessorNames = map(lambda x : preprocessorFormat(x,entry.prefix),uniqueFileNames)

    with open(entry.outputPath, "w", encoding="UTF-8") as writer:
        s = swift.Swift(writer)
        uniqueFileNames=map(s.doubleQoute,uniqueFileNames)
        values = zip(preprocessorNames, uniqueFileNames)

        s.enumeration(entry.enum, values, "String")


if __name__ == '__main__':
    try:
        yamlPath = sys.argv[1]
    except:
        yamlPath = "./python/parser/config.yaml"

    with open(yamlPath, 'r', encoding='UTF-8') as reader:
        data = yaml.load(reader)
        plistData = data["segues"]

        for plist in plistData:
            entry = createEntry(plist["prefix"], plist["output"], plist["enum"], plist["folder"])
            processEntry(entry)

