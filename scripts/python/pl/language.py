from contextlib import contextmanager
import io 
import functools

@contextmanager
def testBuffer():
    buffer = io.StringIO()
    yield buffer
    buffer.seek(0)
    print(buffer.read())

class Language:
    def __init__(self, stream, indentionChar="    ",newLine="\n"):
        self.stream = stream
        self.indentionChar = indentionChar
        self._newLine = newLine
        self.indentionCount = 0
        self.linePrefix = None
        self.lineComment = "//"
        self.multilineCommentStart = "/*"
        self.multilineCommentEnd = " */"
        self.multilineMiddle = " *"

    @contextmanager
    def commentWithBorder(self,boarderSize):
        boarder = self.lineComment*boarderSize
        self.writeLine(boarder)
        self.linePrefix = self.lineComment 
        yield
        self.linePrefix = None
        self.writeLine(boarder)

    @contextmanager
    def multilineComment(self,indent=False):
        with self.pairedItem(self.multilineCommentStart,
                             self.multilineCommentEnd,
                             indent):
            self.linePrefix = self.multilineMiddle
            yield       
            self.linePrefix = None

    @contextmanager
    def indent(self,value=1):
        self.indentionCount += value 
        yield
        self.indentionCount -= value

    def currentIndent(self):
        return self.indentionChar* self.indentionCount 

    @contextmanager
    def pairedItem(self, openingCharacter, closingCharacter, indent= True): 
        self.writeLine(openingCharacter)
        if indent:
            with self.indent() :
                yield
        else :
            yield
        self.writeLine(closingCharacter)

    def enclose(self, openingCharacter, closingCharacter,value):
        return "{0}{2}{1}".format(openingCharacter,closingCharacter,value)

    def writeLine(self,line="",indention=True):
        self.write(line,indention) 
        self.newLine()

    def write(self,line, indention=True):
        if indention:
            lineData = self.currentIndent() + line 
        else :
            lineData = line

        if self.linePrefix :
            lineData = self.linePrefix +" "+ lineData
        self.stream.write(lineData)

    def newLine(self):
        self.stream.write(self._newLine)


class CBased(Language):
    parenthesis = functools.partialmethod(Language.pairedItem,"{","}")
    closedParenthesis = functools.partialmethod(Language.pairedItem,"{","};")

    @contextmanager
    def headerGuard(self,guard):
        self.writeLine("#ifndef "+guard)
        self.define(guard)
        yield
        self.writeLine("#endif //"+guard)

    def define(self, key, value=None):
        if value :
            self.writeLine("#define {0} {1}".format(key,value))
        else :
            self.writeLine("#define {0}".format(key))

    def defineStringValue(self, key, value):
        self.writeLine("#define {0} \"{1}\"".format(key,value))

    def systemInclude(self,value):
        self.writeLine("#include <0>".format(value))

    def localInclude(self,value):
        self.writeLine("#include \"{0}\"".format(value))