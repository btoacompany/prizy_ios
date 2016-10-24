import os
import sys
import pprint
import collections
import functools
import shutil
import time
import fractions
import json
from contextlib import contextmanager

from wand.image import Image
import yaml 

from os.path import dirname
parent = os.path.join(dirname(__file__),"../..")
absParent = os.path.abspath(parent)
sys.path.append(absParent)

from python.wording import wlp
from python.pl import swift

ImageMetadata = collections.namedtuple("ImageMetadata", "fullpath, fullFilename, filename, extension, directory")
LOG_DEBUG = "Debug"
LOG_WARNINGS_ERRORS = "Warnings&Errors"
LOG_LEVEL = LOG_WARNINGS_ERRORS
@contextmanager
def changeDirectory(directory):
    currentDirectory = os.path.abspath(os.curdir)
    os.chdir(directory)
    yield
    os.chdir(currentDirectory)


def parseExcel(excelConfig):
    localizationObj= wlp.excelReader(os.path.abspath(excelConfig["path"]),
                                    sheetName=excelConfig["sheet_name"],
                                    headerLine=int(excelConfig["header_line"]),
                                    keyColumn= excelConfig["key_column_name"],
                                    localizationColumnMapping =excelConfig["localization_column_mapping"])

    return localizationObj

def imageGenerator(imageConfig):
    includeExtension = imageConfig["included_extension"]
    imagePath = os.path.abspath(imageConfig["path"])
    for d, sd, fs in os.walk(imagePath):
        for f in fs:
            filename,extension = os.path.splitext(f)
            if extension in includeExtension:
                fullPath = os.path.join(d,f) 
                yield ImageMetadata(fullPath,f,filename,extension,d)
            else: 
                print(extension, "not found")

def getRelatedData(filename, excelData, fieldName="filename"):
    yieldCount = 0
    for v in excelData.values():
        if v[fieldName].strip() == filename.strip() and (v["iosAttribute"].strip() is not "delete" or v["androidAttribute"].strip() is not "delete"):
            yieldCount += 1
            yield v

    if yieldCount == 0 and LOG_LEVEL in [LOG_DEBUG , LOG_WARNINGS_ERRORS]:
        print("ERROR:", filename, "Not in excel sheet")

def processResize(imagedata, attrib, directory,finalName):
    directory = os.path.abspath(directory)
    finalName = finalName.strip()
    if len(finalName) != 0:
        fileName,ext = os.path.splitext(finalName)
    else :
        fileName,ext = imagedata.filename, imagedata.extension
    with changeDirectory(imagedata.directory):
        for key,values in attrib.items():
            with Image(filename=imagedata.fullFilename) as cloneImg:
            
                if "exact_size" in values:
                    size = values["exact_size"]
                    width, height = list(map(int,size.strip().split("x")))
                elif "resize" in values:
                    size = values["resize"]
                    multiplier, divisor = list(map(int,size.strip().split("/")))
                    width = int(cloneImg.width * multiplier / divisor)
                    height = int(cloneImg.height * multiplier / divisor)
                elif "exact_liquid" in values:
                    size = values["exact_liquid"]
                    width, height = list(map(int,size.strip().split("x")))
                    if height > width:
                        cropRatio = cloneImg.height / height 
                        cropHeight = cloneImg.height 
                        cropWidth = width * cropRatio
                    if width > height:
                        cropRatio = cloneImg.width / width
                        cropWidth = cloneImg.width 
                        cropHeight = height * cropRatio
                    
                    if (cloneImg.width < cropWidth):
                        cropWidth= cloneImg.width
                    if (cloneImg.height < cropHeight):
                        cropHeight= cloneImg.height
                    cloneImg.crop(width=int(cropWidth), height=int(cropHeight), gravity='center')



                if  LOG_LEVEL in [LOG_DEBUG , LOG_WARNINGS_ERRORS] and (cloneImg.width < width or cloneImg.height < height):
                    reason =  "Enlarged dimension {0}x{1} source dimension {2}x{3}".format(
                                width,height, cloneImg.width, cloneImg.height)

                    print("WARNING:",imagedata.fullFilename, reason)
                
                cloneImg.resize(width, height)

                for format in values["file_formats"]:
                    destinationPath = os.path.join(directory,format).format(fileName,ext)
                    d , f = os.path.split(destinationPath)

                    if not os.path.exists(d):
                        os.makedirs(d)

                    with open(destinationPath,"wb") as writer:
                        cloneImg.save(file=writer)
                    if LOG_LEVEL == LOG_DEBUG:
                        print("Output:", destinationPath)

def clearFolders(*folderlist):
    for folder in folderlist:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    time.sleep(2)
    for folder in folderlist:
        if not os.path.exists(folder):
            os.makedirs(folder)

def checkImageData(imagedata, procedure):
    #Check if attribute is skip or delete
    toSkipAttributes = ["skip","delete"]
    if procedure["iosAttribute"] in toSkipAttributes:
        return False, procedure["iosAttribute"] 
    elif procedure["androidAttribute"] in toSkipAttributes:
        return False, procedure["androidAttribute"]

    with changeDirectory(imagedata.directory):
        with Image(filename=imagedata.fullFilename) as img:  
            expectedWidth = int(procedure["width"])
            expectedHeight = int(procedure["height"]) 
            if expectedHeight != img.height or expectedWidth != img.width:
                reason =  "expected dimension {0}x{1} actual dimension {2}x{3}".format(
                                    expectedWidth,expectedHeight,
                                    img.width, img.height)
                return False , reason 

    return True, None

def resizeImages(excelData,outputConfig,imageSettings,imageGeneratorFunc):
    if "android" in outputConfig: 
        clearFolders(outputConfig["android"]["output"])
    if "ios" in outputConfig: 
        clearFolders(outputConfig["ios"]["output"])

    uniqueFilenames = list(set(map(lambda x : x["filename"].strip(),excelData.values())))

    for image in imageGeneratorFunc():
        if image.fullFilename in uniqueFilenames:
            index = uniqueFilenames.index(image.fullFilename)
            del uniqueFilenames[index]

        if LOG_LEVEL == LOG_DEBUG:
            print()
            print("Input:", image.fullFilename)
        
        for procedure in getRelatedData(image.fullFilename,excelData):
            shouldProcess, reason = checkImageData(image,procedure)
            if not shouldProcess:
                if LOG_LEVEL in [LOG_DEBUG , LOG_WARNINGS_ERRORS]:
                    print("WARNING:",image.fullFilename,reason)
                continue
                
            if procedure["os"].strip() in ["ios","both"]:
                folder = outputConfig["ios"]["output"]
                imageSettingKey = "ios_"+procedure["iosAttribute"]

                iosAttribute = imageSettings[imageSettingKey]
                processResize(image,iosAttribute,folder,procedure["rename"])

            if procedure["os"].strip() in ["android","both"]:
                folder = outputConfig["android"]["output"]
                imageSettingKey = "android_"+procedure["androidAttribute"]
                androidAttribute = imageSettings[imageSettingKey]
                processResize(image,androidAttribute,folder,procedure["rename"])

    if LOG_LEVEL in [LOG_DEBUG , LOG_WARNINGS_ERRORS]:
        for filename in uniqueFilenames:
            print("ERROR:" ,filename, "Does not exist")


def createKey(prefix,key):
    if "." in key:
        filename, _ = key.strip().split(".")
        return "IMG_"+filename.upper()
    else :
        return "IMG_"+key.upper()

def getFilenames(listValues,field,default):
    l = []
    for d in listValues:
        n = d[field].strip()
        if len(n)==0:
            n = d[default].strip()
        l.append(n)
    l.sort()
    return l

def createHeader(excelData,outputConfig):
    data= list(excelData.values())
    iosOnly = filter(lambda x : x["os"].strip() in ["ios","both"],data)
    iosOnly = list(filter(lambda x: x["iosAttribute"] not in ["skip","delete"],iosOnly))
    iosOnly = list(map(lambda x: x["finalname"].strip(), iosOnly))

    outputPath = outputConfig["ios"]["header"]["path"]
    prefix = outputConfig["ios"]["header"]["prefix"]

    with open(outputPath,"w", encoding="UTF-8") as writer:
        s = swift.Swift(writer)
        prefixKey = functools.partial(createKey,prefix)
        values = zip(map(prefixKey,iosOnly), map(s.doubleQoute,iosOnly))
        s.enumeration("Images",values,"String")

def postprocessingContentJSON(folderPath):
    for entry in os.scandir(folderPath):
        if entry.name.endswith('.imageset') and not entry.is_file():
            imageSetContentJson(os.path.join(folderPath,entry.name))
        elif entry.name.endswith('.appiconset') and not entry.is_file():
            appiconSetContentJson(os.path.join(folderPath,entry.name))
        elif entry.name.endswith('.launchimage') and not entry.is_file():
            launchSetContentJson(os.path.join(folderPath,entry.name))

def launchSetContentJson(path):
    data = {
      "images" : [
            {"extent" : "full-screen", "idiom" : "iphone", "subtype" : "736h", "filename" : "iphone6Plus.png", "minimum-system-version" : "8.0", "orientation" : "portrait", "scale" : "3x"},
            {"extent" : "full-screen", "idiom" : "iphone", "subtype" : "667h", "filename" : "iphone6.png", "minimum-system-version" : "8.0", "orientation" : "portrait", "scale" : "2x"},
            {"orientation" : "portrait", "idiom" : "iphone", "filename" : "iphone4.png", "extent" : "full-screen", "minimum-system-version" : "7.0", "scale" : "2x"},
            {"extent" : "full-screen", "idiom" : "iphone", "subtype" : "retina4", "filename" : "iphoneSE.png", "minimum-system-version" : "7.0", "orientation" : "portrait", "scale" : "2x"},
            {"orientation" : "portrait", "idiom" : "ipad", "filename" : "tablet-portrait.png", "extent" : "full-screen", "minimum-system-version" : "7.0", "scale" : "1x"},
            {"orientation" : "landscape", "idiom" : "ipad", "filename" : "tablet-landscape.png", "extent" : "full-screen", "minimum-system-version" : "7.0", "scale" : "1x"},
            {"orientation" : "portrait", "idiom" : "ipad", "filename" : "tablet-portrait@2x.png", "extent" : "full-screen", "minimum-system-version" : "7.0", "scale" : "2x"},
            {"orientation" : "landscape", "idiom" : "ipad", "filename" : "tablet-landscape@2x.png", "extent" : "full-screen", "minimum-system-version" : "7.0", "scale" : "2x"}
      ],
      "info" : {
        "version" : 1,
        "author" : "xcode"
      }
    }

    _, filename = os.path.split(path)
    filename, _ = os.path.splitext(filename)

    for d in data["images"]:
        d["filename"]= d["filename"].format(filename)

        if not os.path.exists(os.path.join(path,d["filename"])):
            print (d["filename"] , "does not exist")

    with open(os.path.join(path,"Contents.json"),"w",encoding = "utf-8") as writer:
        json.dump(data,writer,indent=4)

def appiconSetContentJson(path):
    data = {
      "images" : [
        {"idiom" : "iphone", "size" : "20x20", "filename" : "{0}-20@2x.png", "scale" : "2x"},
        {"idiom" : "iphone", "size" : "20x20", "filename" : "{0}-20@3x.png", "scale" : "3x"},
        {"idiom" : "ipad", "size" : "20x20", "filename" : "{0}-20@2x.png", "scale" : "2x"},
        {"size" : "60x60", "idiom" : "iphone", "filename" : "{0}-60@3x.png", "scale" : "3x"},
        {"idiom" : "ipad", "size" : "20x20", "filename" : "{0}-20.png", "scale" : "1x"},
        {"size" : "29x29", "idiom" : "iphone", "filename" : "{0}-Small@2x.png", "scale" : "2x"},
        {"size" : "29x29", "idiom" : "iphone", "filename" : "{0}-Small@3x.png", "scale" : "3x"},
        {"size" : "40x40", "idiom" : "iphone", "filename" : "{0}-40@2x.png", "scale" : "2x"},
        {"size" : "40x40", "idiom" : "iphone", "filename" : "{0}-40@3x.png", "scale" : "3x"},
        {"size" : "60x60", "idiom" : "iphone", "filename" : "{0}-60@2x.png", "scale" : "2x"},
        {"size" : "29x29", "idiom" : "ipad", "filename" : "{0}-Small.png", "scale" : "1x"},
        {"size" : "29x29", "idiom" : "ipad", "filename" : "{0}-Small@2x.png", "scale" : "2x"},
        {"size" : "40x40", "idiom" : "ipad", "filename" : "{0}-40.png", "scale" : "1x"},
        {"size" : "40x40", "idiom" : "ipad", "filename" : "{0}-40@2x.png", "scale" : "2x"},
        {"size" : "76x76", "idiom" : "ipad", "filename" : "{0}-76.png", "scale" : "1x"},
        {"size" : "76x76", "idiom" : "ipad", "filename" : "{0}-76@2x.png", "scale" : "2x"},
        {"size" : "83.5x83.5", "idiom" : "ipad", "filename" : "{0}-83.5@2x.png", "scale" : "2x"}
      ],
      "info" : {
        "version" : 1,
        "author" : "xcode"
      }
    }

    _, filename = os.path.split(path)
    filename, _ = os.path.splitext(filename)

    for d in data["images"]:
        d["filename"]= d["filename"].format(filename)

        if not os.path.exists(os.path.join(path,d["filename"])):
            print (d["filename"] , "does not exist")

    with open(os.path.join(path,"Contents.json"),"w",encoding = "utf-8") as writer:
        json.dump(data,writer,indent=4)

def imageSetContentJson(path):
    images = []
    for entry in os.scandir(path):
        if entry.is_file():
            name, _ = os.path.splitext(entry.name)
            scale = "1x"
            idiom = "universal"
            if "@" in name:
                filename, description = name.split("@")
                if "~" in description:
                    scale , idiom = description.split("~")
                else:
                    scale = description
            elif "~" in name:
                _, idiom = name.split("~")
                
            images.append({
                "idiom":idiom,
                "scale":scale,
                "filename":entry.name
                })

    contents = {"images":images, "info":{"version":1,"author":"xcode"}}
    with open(os.path.join(path,"Contents.json"),"w",encoding = "utf-8") as writer:
        json.dump(contents,writer,indent=4)

def main(imageSettings, config):
    inputConfig = config["input"]
    outputConfig = config["output"]
    excelData = parseExcel(inputConfig["excel"])

    resizeImages(excelData,outputConfig,imageSettings,functools.partial(imageGenerator,inputConfig["image"]))
    
    createHeader(excelData,outputConfig)
    postprocessingContentJSON(outputConfig["ios"]["output"])

if __name__=="__main__":
    try:
        _, imageSettingsPath, configPath, *_ = sys.argv
    except:
        imageSettingsPath = os.path.abspath(r"./python/image/image_settings.yaml")
        configPath = os.path.abspath(r"./python/image/config.yaml")

    with open(imageSettingsPath, 'r',encoding = 'UTF-8') as reader:
        imageSettings = yaml.load(reader)

    with open(configPath, 'r',encoding = 'UTF-8') as reader:
        config = yaml.load(reader)

    main(imageSettings,config)