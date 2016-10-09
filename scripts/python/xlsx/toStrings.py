import sys
import os
import pprint

import yaml
import html

from python.wording import wlp
from python.pl import swift
def unicodeiOS(key,value):
    newValue = ""
    value = value.replace('\"','"')
    value = value.replace("%s","%@")

    key = key.replace(".","_")

    ALLOWED_SYMBOLS = " !@`+;*:}{[]#$%&'()=-~^|\\_?><,./"
    for c in value:
        if c.isalnum() or c in ALLOWED_SYMBOLS:
            newValue += c
        elif c == '"':
            newValue += "\\\""
        else :
            newValue += c
            """
            unicodeValue = ord(c)
            hexStr = hex(unicodeValue)[2::] # ---> 0xXXXXXXX
            v = "\\u{0}{1}".format("0"*(4-len(hexStr)),hexStr)
            newValue +=v"""
    return key,html.unescape(newValue)

def createKey(key):
    return "WRD_"+key.upper()

def createHeader(localizationObj,outputPath):
    keys = list(localizationObj.keys())
    keys.sort()
    with open(outputPath,"w", encoding="UTF-8") as writer:
        s = swift.Swift(writer)
        values = zip(map(createKey,keys), keys)
        s.enumeration("Wording",values,"String")


if __name__ == "__main__":
    try:
        yamlPath = sys.argv[1]
    except:
        yamlPath = "./config.yaml"

    with open(yamlPath, 'r', encoding='UTF-8') as reader:
        yamlList = yaml.load(reader)

    for data in yamlList:
        inputData = data["input"]
        sheetName = inputData["sheet"]
        # print(os.path.abspath(inputData["excel_path"]))
        localizationObj = wlp.excelReader(os.path.abspath(inputData["xlsx"]),
                                          sheetName=sheetName,
                                          headerLine=int(inputData["start_row"]),
                                          keyColumn=inputData["mapping"]["ID"],
                                          localizationColumnMapping=inputData["mapping"])

        output = data["output"]
        iosMapping = output["iOS_SINGLE"]
        filename = os.path.basename(os.path.abspath(inputData["xlsx"]))

        wlp.iOSWriter(localizationObj, filename, iosMapping, keyValueTransform=unicodeiOS)
        createHeader(localizationObj,output["iOS_Header"])








