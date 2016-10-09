from contextlib import contextmanager
import language

@contextmanager
def createJavaFile(filePath,indentionChar="    ",newLine="\n"):
    with open(filePath, "w") as writer :
        yield Java(writer, indentionChar, newLine)

class Java(language.CBased):
    @contextmanager
    def createPublicClass(self,className, extend=None, interfaces=None):
        self.write("public class "+ className)
        if extend:
            self.write(" extends "+extend, indention=False)
        if interfaces:
            interfaceStr = " ,".join(interfaces)
            self.write(" implements "+interfaceStr)
        
        with self.parenthesis():
            yield

    def Import(self,value):
        self.writeLine("import {0};".format(value))

    def publicStaticString(self,variable,value):
        self.writeLine("public static final String {0} = \"{1}\";".format(variable,value))

if __name__ == '__main__':
    with language.testBuffer() as buffer:
        java = Java(buffer)
        java.Import("System.out")
        with java.createPublicClass("Test", extend="B") :
            java.publicStaticString("DDDD","VVV")
            java.publicStaticString("DDDD","VVV")
            java.publicStaticString("DDDD","VVV")

        