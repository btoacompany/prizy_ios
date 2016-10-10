import sys
import xlrd
import os
import csv
import json
import io

from python.wording import template

from collections import OrderedDict
import xml.etree.ElementTree as ET
import math
import pprint
#ONLY FOR PYTHON 3 ABOVE

#supported  output platform 
IOS       = "IOS"
WINRT     = "WINRT"
ANDROID   = "ANDROID"

#Available Localization #MOREpaMORE!
ENGLISH   = "ENGLISH"
JAPANESE  = "JAPANESE"
FRENCH    = "FRENCH"
DUTCH     = "DUTCH"
SPANISH   = "SPANISH"
GERMAN    = "GERMAN"

KEY = "key"

#########################################
#HELPER FUNCTIONS 
#########################################
def sort(localizationObj):
    def Sort(dict1):
        d = OrderedDict()
        k = list(dict1.keys())
        k.sort()
        for key in k :
            d[key] = dict1[key]
        return d

    keys = list(localizationObj.keys())
    keys.sort()
    sortedD = OrderedDict()
    for k in keys:
        sortedD[k]= Sort(localizationObj[k])
    return sortedD

def removeLanguage(localizationObject ,*languages):
    pass

def valueFormat(val):
    valType =type(val)
    if str== valType:
        return val
    if int == valType:
        return str(val)
    if float == valType and math.floor(val) == val:
        return str(math.floor(val))
    return str(val)

def writeToFile(localizationObj,sheetName,filePath,key1,key2,bodyTemplate,lineTemplate,transformFunc=None ):
    body = io.StringIO()
    for values in localizationObj.values():
        value1 = values[key1]
        value2 = values[key2]
        if transformFunc :
            value1,value2 = transformFunc(value1,value2)
        
        body.write(lineTemplate.format(value1,value2))

    dirPath = os.path.dirname(os.path.abspath(filePath))
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(filePath,'w',encoding='UTF-8') as writer:
        writer.write(bodyTemplate.format(body.getvalue(),sheetName))

def translate(strValue,translateMapping):
    strValue =str(strValue)

    for key ,value in translateMapping.items():
        if key in strValue :
            strValue = strValue.replace(key,value)

    return strValue

def _parseXLIFF(xliffPath,defaultLanguage, language,localizationFileMap={}):
    tree = ET.parse(xliffPath)
    root = tree.getroot()
    namespace = "{urn:oasis:names:tc:xliff:document:1.2}"
    files =  root.findall(namespace+'file')
    for f in files :
        fileName = f.get("original")
    
        if fileName not in  localizationFileMap:
            localizationFileMap[fileName]=OrderedDict()
        fileMap = localizationFileMap[fileName]
   
        for word in f.getiterator(namespace+"trans-unit"):

            targetNode = word.find(namespace+"target")
            sourceNode = word.find(namespace+"source")
            key = word.get("id")
           
            if targetNode is None:
                continue#skip nodes with no translation
            if key not in fileMap:
                fileMap[key] = OrderedDict({KEY:key})
            if defaultLanguage not in  fileMap[key]:
                fileMap[key][defaultLanguage]=sourceNode.text
            fileMap[key][language]=targetNode.text

    return localizationFileMap

def _parseAndroidXml(filePath, language,localizationObj = OrderedDict(),translateMapping=None):
    tree = ET.parse(filePath)
    root = tree.getroot()
    for stringNode in root.getiterator("string"):
        key = stringNode.attrib["name"].upper()
        value = stringNode.text

        if value is None :
            value =""
        elif translateMapping : 
            value = translate(value,translateMapping)

        if key not in localizationObj:
            localizationObj[key] = OrderedDict({language:value})
        else :
            localizationObj[key][language]=value

        if KEY not in localizationObj[key]:
            localizationObj[key][KEY]=key

    return localizationObj

def _parseWinRTXml(filePath, language,localizationObj = OrderedDict()):
    tree = ET.parse(filePath)
    root = tree.getroot()

    for stringNode in root.getiterator("data"):
        key = stringNode.attrib["name"]
        value = stringNode.find("value").text

        if key not in localizationObj:
            localizationObj[key] = OrderedDict({language:value})
        else :
            localizationObj[key][language]=value

    return localizationObj

#########################################
#XLS FUNCTIONS 
#########################################
def excelSheetReader(worksheet,headerLine,keyColumn, localizationColumnMapping,localizationObj=OrderedDict()):
    # get header colNumber
    headerRow= worksheet.row_values(headerLine-1)
    indexMapping = OrderedDict()
    indexMapping["key"] = headerRow.index(keyColumn)

    for key, data in localizationColumnMapping.items():
        indexMapping[key] = headerRow.index(data)

    #process localization body

    for columndata in map(worksheet.row_values,range(headerLine,worksheet.nrows )):
        localizationData=OrderedDict()
        for key,index in indexMapping.items():
            localizationData[key]= valueFormat(columndata[index])
        localizationKey = localizationData[KEY]
        # del localizationData[KEY]
        localizationObj[localizationKey]=localizationData
    return localizationObj

def excelReaderAllSheet(excelFilePath, headerLine,keyColumn, localizationColumnMapping,ignoreSheets = [],localizationObj=OrderedDict()):
    with xlrd.open_workbook(excelFilePath) as workbook :
        data = {}
        for sheet in workbook.sheets():
            name = sheet.name
            if name in ignoreSheets:
                continue
            value = excelSheetReader(sheet,headerLine,keyColumn, localizationColumnMapping,OrderedDict())
            data[name] = value
        return data

def excelReader(excelFilePath, sheetName, headerLine, keyColumn, localizationColumnMapping, localizationObj=OrderedDict()):
    with xlrd.open_workbook(excelFilePath) as workbook :
        # get the first sheet after changelogs
        worksheet = workbook.sheet_by_name(sheetName)
        return excelSheetReader(worksheet,headerLine,keyColumn, localizationColumnMapping,localizationObj)
       

def csvWriter(localizationObj,excelFilePath,keyColumn, localizationColumnMapping):
    dirPath = os.path.dirname(os.path.abspath(excelFilePath))
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    with open(excelFilePath, 'w',encoding='UTF-16') as csvfile:
        #
        fieldnames= list(localizationColumnMapping.values())
        fieldnames.insert(0,KEY)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n',delimiter=',', quoting=csv.QUOTE_ALL )#,delimiter=',',quotechar='|', quoting=csv.QUOTE_ALL)
        
        writer.writeheader()
        for values in localizationObj.values():
            writer.writerow (values)

#########################################
#JSON FUNCTIONS 
#########################################
def jsonWriter(localizationObj,jsonPath):
    if len(list(localizationObj.keys())) == 0:
        return
    dirPath = os.path.dirname(os.path.abspath(jsonPath))
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(jsonPath, 'w',encoding='UTF-8') as writer:
        json.dump(localizationObj,writer,indent=4, ensure_ascii=False)

def jsonReader(jsonPath ):
    with open(jsonPath, 'r',encoding = 'UTF-8') as reader:
        return json.load(reader,object_pairs_hook=Localization)

#########################################
#iOS FUNCTIONS 
#########################################
def createObjCEnumFromList(keys,sheetName,filePath,transformFunc=None):
    fileName = os.path.basename(filePath)

    headerGuard = "_{0}_".format(fileName.replace(".","_").upper())

    body = io.StringIO()
    for key in keys[0:-1]:
        if transformFunc != None:
            newKey = transformFunc(key)
            body.write(template.objCEnumLineTemplate.format(newKey))
        else :
            body.write(template.objCEnumLineTemplate.format(key))
    key = keys[-1]
    if transformFunc != None:
        newKey = transformFunc(key)
        body.write(template.objCEnumLineEndTemplate.format(newKey))
    else :
        body.write(template.objCEnumLineEndTemplate.format(key))


    
    dirPath = os.path.dirname(os.path.abspath(filePath))
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(filePath,'w',encoding='UTF-8') as writer:
        writer.write(template.objCEnumBodyTemplate.format(fileName,headerGuard,fileName.replace(".h",""),body.getvalue(),"{","}"))

def createObjCHeaderFromList(keys,sheetName,filePath,transformFunc=None):
    fileName = os.path.basename(filePath)

    headerGuard = "_{0}_".format(fileName.replace(".","_").upper())
    bodytemplate = template.objCBodyTemplate.format(fileName,headerGuard,"{0}","{1}")

    body = io.StringIO()
    for key in keys:
        if transformFunc != None:
            key, value = transformFunc(key)
            body.write(template.objCLineTemplate.format(key,value))
        else :
            body.write(template.objCLineTemplate.format(key,key))
    
    dirPath = os.path.dirname(os.path.abspath(filePath))
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(filePath,'w',encoding='UTF-8') as writer:
        writer.write(bodytemplate.format(body.getvalue(),sheetName))

def translate(strValue,translateMapping):
    strValue =str(strValue)

    for key ,value in translateMapping.items():
        if key in strValue :
            strValue = strValue.replace(key,value)

    return strValue
def createObjCHeaderFile(localizationObj,sheetName,filePath):
    fileName = os.path.basename(filePath)

    headerGuard = "_{0}_".format(fileName.replace(".","_").upper())
    bodytemplate = template.objCBodyTemplate.format(fileName,headerGuard,"{0}","{1}")

    writeToFile(localizationObj,sheetName,filePath,KEY,KEY,bodytemplate,template.objCLineTemplate)

def iOSWriter(localizationObj,sheetName,localizationPathMap,keyValueTransform=None):
    for language, filePath in localizationPathMap.items():
        writeToFile(localizationObj,sheetName,filePath,KEY,language,template.iOSBodytemplate,template.iOSLineTemplate,transformFunc=keyValueTransform)

def iOSReader(defaultLanguage,localizationPathMap):
    localizationMap = OrderedDict()
    for currentLanguage,value in localizationPathMap.items():
        localizationMap =_parseXLIFF(value,defaultLanguage,currentLanguage,localizationMap)
    return localizationMap

#########################################
#ANDROID FUNCTIONS 
#########################################
def createObJavaEnumClasssFromList(keys, filePath, packageName, project, inheritClass = None, importData = [], transformFunc = None):
    fileName = os.path.basename(filePath)
    
    body = io.StringIO()
    for key in keys:
        if transformFunc != None:
            newKey,value = transformFunc(key)
            body.write(template.javaLineTemplate.format(newKey,value))
        else :
            body.write(template.javaLineTemplate.format(key,key))

    imports = io.StringIO()
    for importValue in importData:
            imports.write(template.javaImportTemplate.format(importValue))

    classNameValue = os.path.basename(filePath)

    if inheritClass != None:
        className = template.javaClassExtend.format(classNameValue.replace(".java",""),inheritClass)
    else :
        className = classNameValue.replace(".java","")

    dirPath = os.path.dirname(os.path.abspath(filePath))
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(filePath,'w',encoding='UTF-8') as writer:
        imports = imports.getvalue()
        body = body.getvalue()
        writer.write(template.javaBodyTemplate.format(classNameValue,project,packageName,imports,className,body,"{","}"))

def androidWriter(localizationObj,sheetName,localizationPathMap,addFormattedField=True,translateMapping={"'":"\\'"},keyValueTransform=None):

    def transform(key,value):
        if keyValueTransform:
            key,value = keyValueTransform(key,value)
            
        if addFormattedField and ("%" in value  or "@" in value):
            key = '{0}" formatted="false'.format(key)        

        if translateMapping:
            value = translate(value,translateMapping)

        return key,value

    bodyTemplate = template.androidBodytemplate.format("{0}",sheetName )
    for language, filePath in localizationPathMap.items():
        writeToFile(localizationObj,sheetName,filePath,KEY,language,bodyTemplate,template.androidLineTemplate,transformFunc=transform)

def androidReader(localizationPathMa,translateMapping={"\\'":"'"}):
    localizationObj = OrderedDict()
    for currentLanguage,filePath in localizationPathMap.items():
        localizationObj =_parseAndroidXml(filePath,currentLanguage,localizationObj,translateMapping)
    return localizationObj


    for language, filePath in localizationPathMap.items():     
        writeToFile(localizationObj,sheetName,filePath,KEY,language,template.winRtBodyTemplate,template.winRtLineTemplate)

#########################################
#HELPER FUNCTIONS 
#########################################
def winRTWriter(localizationObj,sheetName,localizationPathMap):
    def transform(key,value):
        indexCount = 0
        percent_d = "%d"
        while percent_d in value: 
            index = value.find(percent_d)
            newString = "{"+str(indexCount)+"}"
            value = value[0:index] +newString+ value[index+2::]
            indexCount +=1
        return key,value

    for language, filePath in localizationPathMap.items():     
        writeToFile(localizationObj,sheetName,filePath,KEY,language,template.winRtBodyTemplate,template.winRtLineTemplate,transformFunc=transform)

def winRTReader(localizationPathMap):
    localizationObj = OrderedDict()
    for currentLanguage,filePath in localizationPathMap.items():
        localizationObj =_parseWinRTXml(filePath,currentLanguage,localizationObj)
    return localizationObj

#########################################
#GENERIC WRITE FUNCTIONS 
#########################################
__writerMapping={
                 IOS     : iOSWriter,
                 ANDROID : androidWriter ,
                 WINRT   : winRTWriter  
                 }

def write(writerType,localizationObj,sheetName,localizationPathMap):
    return __writerMapping[writerType](localizationObj,sheetName,localizationPathMap)
