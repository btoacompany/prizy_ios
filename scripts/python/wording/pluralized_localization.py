import plistlib
import pprint
import collections
class PluralizedLocale:
	def __init__(self, transformKeyFunc):
		self.mapping = collections.OrderedDict()
		self.mappingTransfromFunc= transformKeyFunc

	def add(self, key, value):
		key, pluralType = self.mappingTransfromFunc(key)
		pluralDict = None

		if key in self.mapping:
			pluralDict = self.mapping[key]
		else :
			pluralDict = collections.OrderedDict()

		pluralDict[pluralType] = value
		self.mapping[key] =pluralDict 

	def writeToiOS(self, languageToFileMapping, transformValueFunc=None):
		#pprint.pprint(self.mapping)
		for langauge, filePath in languageToFileMapping.items():
			#print (langauge, filePath)
			self.writeToiOSFile(filePath,langauge,transformValueFunc)

	def writeToiOSFile(self, filePath, language,transformValueFunc=None):		
		data = {}
		for k in self.mapping.keys():
			v = self.iosEntry(k,language,transformValueFunc)
			data[k]=v

		with open(filePath, 'wb') as fp:
			plistlib.dump(data, fp)

	def iosEntry(self,key,langauge,transformValueFunc=None):
		data = {
				"NSStringLocalizedFormatKey" : "%#@d@",
				"d" : {
					"NSStringFormatSpecTypeKey": "NSStringPluralRuleType",
					"NSStringFormatValueTypeKey":"d"
					}
				}
		pluralMapping = self.mapping[key]	
		for k , v in pluralMapping.items():
			value = v[langauge]
			if "%$d" in value:
				#print (value)
				index = value.index("%$d")
				text = value[:index]
				#print( text+"%#@d@")
				data ["NSStringLocalizedFormatKey" ] =  text+"%#@d@"
				value = value[index::] 
				value = value.replace("%$d","%d")
			#print (value)
			if len(value.strip())==0 : 
				continue
			if transformValueFunc!=None:
				value = transformValueFunc(value)
			data["d"][k.lower()]=value
		return  data
 

	def writeToAndroid(self, languageToFileMapping, pluralKeyValueTransformFunc=None):
		for langauge, filePath in languageToFileMapping.items():
			self.writeToAndroidFile(filePath,langauge,pluralKeyValueTransformFunc)

	def writeToAndroidFile(self, filePath, language,pluralKeyValueTransformFunc=None):		
		data = """<?xml version="1.0" encoding="utf-8"?>
<resources>
"""
		for k in self.mapping.keys():
			data+= self.androidEntry(k,language,pluralKeyValueTransformFunc)
		data+= "</resources>"

		with open(filePath, "w",encoding='UTF-8') as writer:
			writer.write(data)

	def androidEntry(self,key,langauge,pluralKeyValueTransformFunc=None):
		rowTemplate = '	<plurals name="{0}">\n{1}	</plurals>\n'
		pluralTemplate = '		<item quantity="{0}">{1}</item>\n'
		pluralMapping = self.mapping[key]	
		entries = ""
		for pluralKey , values in pluralMapping.items():
			value = values[langauge].replace("%$d","%d")
			if len(value.strip())== 0 :
				continue
			if pluralKeyValueTransformFunc!=None:
				pluralKey,value = pluralKeyValueTransformFunc(pluralKey,value)
			entries += pluralTemplate.format(pluralKey, value)
		rowData = rowTemplate.format(key,entries)	
		return  rowData

