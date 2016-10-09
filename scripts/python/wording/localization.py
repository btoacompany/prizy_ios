import collections
import os

from python.wording import wlp

class Localization:
    def __init__(self):
        self.data = collections.OrderedDict()
        self.languages = []
        self.localizationName = ""

    def addEntry(self, entry):
        self.data[entry[wlp.key]] = entry

    def sort(self):
        self.data = wlp.sort(self.data)      
          
#######################################
# STATIC IMPORT FUNCTIONS 
#######################################
    @classmethod
    def importFromExcel(classSelf, path,sheetName,headerlineNumber,keyColumn,columnMapping):
        localizationObj = Localization()
        localizationObj.localizationName= sheetName
        localizationObj.languages = list(columnMapping.keys())
        localizationObj.data = wlp.excelReader(path,sheetName,headerlineNumber,keyColumn, columnMapping)
        return localizationObj
    
    @classmethod
    def importFromJson(classSelf,path,localizationName="Json Resource"):
        localizationObj = Localization()
        localizationObj.localizationName = localizationName
        localizationObj.data = wlp.jsonReader(path)
        data = localizationObj.data.items().next()
        localizationObj.languages = list(data.keys())
        return localizationObj
        
    @classmethod
    def importFromIOS(classSelf,pathMapping,defaultLanguage):
        data = wlp.iOSReader(defaultLanguage,pathMapping) 
        objs = {}
        for key ,value in data.items():
            fileName = os.path.basename(key)
            localizationObj = Localization()
            localizationObj.localizationName = fileName
            localizationObj.data = value
            localizationObj.languages = list(pathMapping.keys())
            localizationObj.languages.insert(0,defaultLanguage)
            objs[fileName] = localizationObj

        return objs 
        
    @classmethod
    def importFromAndroid(classSelf,pathMapping, localizationName="Android Resource"):
        localizationObj = Localization()
        localizationObj.localizationName = localizationName
        localizationObj.languages = list(pathMapping.keys())
        localizationObj.data = wlp.androidReader(pathMapping)
        return localizationObj
        
    @classmethod
    def importFromWinRT(classSelf,pathMapping,localizationName="WinRT Resource"):
        localizationObj = Localization()
        localizationObj.localizationName = localizationName
        localizationObj.languages = list(pathMapping.keys())
        localizationObj.data = wlp.winRTReader(pathMapping)
        return localizationObj
        
#######################################
# EXPORT FUNCTIONS 
#######################################
    def exportToIOS(self,pathMapping):
        wlp.iOSWriter(self.data,self.localizationName,pathMapping)

    def exportToAndroid(self,pathMapping):
        wlp.androidWriter(self.data,self.localizationName,pathMapping) 

    def exportToWinRT(self,pathMapping):
        wlp.iOSWriter(self.data,self.localizationName,pathMapping) 

    def exportToCSV(self,path,keyColumn, localizationColumnMapping):
        wlp.csvWriter(self.data,path,keyColumn,localizationColumnMapping) 

    def exportToJson(self,path):
        wlp.jsonWriter(self.data,path)

    def export(self,platform,pathMapping):
        wlp.write(platform,self.data,self.localizationName,pathMapping)

    def exportObjectiveCHeader(self,path):
        wlp.createObjCHeaderFile(self.data,self.localizationName,path)

        
# SAMPLE CODE 
if __name__=="__main__":
    wordingListAlphaObj =  Localization2.importFromExcel( path = "RISO_SmartDeviceApp_WordingList.xlsx",
                                                         sheetName ="WordingList_Alpha1",
                                                         headerlineNumber= 13,
                                                         key="ID",
                                                         columnMapping= {
                                                                            ENGLISH  : "ENGLISH" ,
                                                                            JAPANESE : "?????????",
                                                                            FRENCH   : "???????????????"  
                                                                        })
    wordingListAlphaObj.exportToCSV("wording_list.csv")
    wordingListAlphaObj.exportToJson("wordin_list.json")

    wordingListAlphaObj.exportToWinRT({
                                        ENGLISH  : "output/winrt/en-US/Resources.resw",
                                        JAPANESE : "output/winrt/ja-JP/Resources.resw",
                                        FRENCH   : "output/winrt/fr-FR/Resources.resw"
                                    })

    wordingListAlphaObj.exportToAndroid({
                                        ENGLISH  : "output/android/res/values/strings.xml",
                                        JAPANESE : "output/android/res/values-ja/strings.xml",
                                        FRENCH   : "output/android/res/values-fr/strings.xml"
                                        })

    wordingListAlphaObj.exportToIOS({
                                        ENGLISH  :  "output/ios/AppStrings/en.lproj/Localizable.strings",
                                        JAPANESE :  "output/ios/AppStrings/ja.lproj/Localizable.strings",
                                        FRENCH   :  "output/ios/AppStrings/fr.lproj/Localizable.strings"
                                    })

    wordingListAlphaObj.exportObjectiveCHeader("output/iOS/AppStrings.h")

