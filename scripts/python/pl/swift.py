from contextlib import contextmanager
import functools

from . import language

@contextmanager
def createObjectiveCFile(filePath,indentionChar="    ",newLine="\n"):
    with open(filePath, "w") as writer :
        yield Swift(writer, indentionChar, newLine)

class Swift(language.Language):
    parenthesis = functools.partialmethod(language.Language.pairedItem, "{", "}")
    doubleQoute = functools.partialmethod(language.Language.enclose, '"', '"')

    def enumeration(self,name, values, enumType = None, indentCount=1):
        if enumType:
            self.write("enum {0}: {1} ".format(name,enumType))
        else :
            self.write("enum {0}".format(name))

        with self.parenthesis():

            for value in values:
                if isinstance(value,str):
                    self.writeLine("case {0}".format(value))
                else :
                    key, value = value
                    self.writeLine("case {0}={1}".format(key,value))




if __name__ == '__main__':
    with language.testBuffer() as buffer:
        swift = Swift(buffer)
        values = ["north","south","east","west"]
        pair = zip(values,map(lambda x: swift.doubleQoute(x),values))

        swift.enumeration("Compass",pair,"String")