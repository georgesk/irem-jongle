from PyQt5.QtGui import QFont, QFontMetrics, QColor
from PyQt5.Qsci import QsciScintilla, QsciLexerPython

class CodeEdit(QsciScintilla):
    def __init__(self, parent=None):
        QsciScintilla.__init__(self,parent)
        # Set the default font
        font = QFont('Courier')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Brace matching: enable for a brace immediately before or after
        # the current position
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

        # Set Python lexer
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)


from PyQt5.QtWidgets import QApplication
import sys
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CodeEdit()
    editor.show()
    editor.setText(open(sys.argv[0]).read())
    app.exec_()
