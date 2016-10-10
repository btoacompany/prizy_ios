from contextlib import contextmanager
from . import language

@contextmanager
def createObjectiveCFile(filePath,indentionChar="    ",newLine="\n"):
    with open(filePath, "w") as writer :
        yield ObjectiveC(writer, indentionChar, newLine)

class ObjectiveC(language.CBased):
    def defineStringValue(self, key, value):
        self.writeLine("#define {0} @\"{1}\"".format(key,value))

    def enumeration(self, name, values, isCounted= False, indentCount=1):
        self.write("typedef NS_ENUM(NSInteger, {0})".format(name))
        with self.closedParenthesis():
            for i, v in enumerate(values):
                if i==0:
                    self.write(v)
                else :
                    if isCounted:
                        self.write(","+self.indentionChar*indentCount, indention=False)
                        self.writeLine(self.lineComment+" "+str(i), indention=False)
                        self.write(v)
                    else :
                        self.writeLine(",",indention=False)
                        self.write(v)  
            self.newLine()         

    def systemImport(self,value):
    	self.writeLine("@import {0};".format(value))

    def localImport(self,value):
    	self.writeLine("#import \"{0}\"".format(value))


if __name__ == '__main__':
    with language.testBuffer() as buffer:
        objC = ObjectiveC(buffer)
        objC.localImport("Foundation.h")
        with objC.multilineComment() :
            objC.writeLine("This is a comment")
            objC.writeLine("This is a comment")
            objC.writeLine("This is a comment")
            objC.writeLine("This is a comment")
        objC.writeLine()
        with objC.headerGuard("TEST_H"):
            objC.defineStringValue("DEBUG", 3.448484)
            values = map(lambda x: "Test"+hex(x), range(100))
            objC.enumeration("TestEnum", values, isCounted=True, indentCount=1)
