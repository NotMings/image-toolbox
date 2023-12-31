# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QProgressBar,
    QPushButton, QSizePolicy, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_toolBoxMainWindow(object):
    def setupUi(self, toolBoxMainWindow):
        if not toolBoxMainWindow.objectName():
            toolBoxMainWindow.setObjectName(u"toolBoxMainWindow")
        toolBoxMainWindow.resize(825, 236)
        self.actionAbout = QAction(toolBoxMainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(toolBoxMainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.formLayout = QFormLayout(self.centralwidget)
        self.formLayout.setObjectName(u"formLayout")
        self.inputFolderHorizontalLayout = QHBoxLayout()
        self.inputFolderHorizontalLayout.setObjectName(u"inputFolderHorizontalLayout")
        self.inputFolderlabel = QLabel(self.centralwidget)
        self.inputFolderlabel.setObjectName(u"inputFolderlabel")

        self.inputFolderHorizontalLayout.addWidget(self.inputFolderlabel)

        self.inputFolderlineEdit = QLineEdit(self.centralwidget)
        self.inputFolderlineEdit.setObjectName(u"inputFolderlineEdit")
        self.inputFolderlineEdit.setMinimumSize(QSize(500, 0))

        self.inputFolderHorizontalLayout.addWidget(self.inputFolderlineEdit)

        self.inputFolderPushButton = QPushButton(self.centralwidget)
        self.inputFolderPushButton.setObjectName(u"inputFolderPushButton")

        self.inputFolderHorizontalLayout.addWidget(self.inputFolderPushButton)

        self.recursiveloadingCheckBox = QCheckBox(self.centralwidget)
        self.recursiveloadingCheckBox.setObjectName(u"recursiveloadingCheckBox")

        self.inputFolderHorizontalLayout.addWidget(self.recursiveloadingCheckBox)


        self.formLayout.setLayout(0, QFormLayout.SpanningRole, self.inputFolderHorizontalLayout)

        self.outputFolderHorizontalLayout = QHBoxLayout()
        self.outputFolderHorizontalLayout.setObjectName(u"outputFolderHorizontalLayout")
        self.outputFolderlabel = QLabel(self.centralwidget)
        self.outputFolderlabel.setObjectName(u"outputFolderlabel")

        self.outputFolderHorizontalLayout.addWidget(self.outputFolderlabel)

        self.outputFolderlineEdit = QLineEdit(self.centralwidget)
        self.outputFolderlineEdit.setObjectName(u"outputFolderlineEdit")
        self.outputFolderlineEdit.setMinimumSize(QSize(500, 0))

        self.outputFolderHorizontalLayout.addWidget(self.outputFolderlineEdit)

        self.outputFolderPushButton = QPushButton(self.centralwidget)
        self.outputFolderPushButton.setObjectName(u"outputFolderPushButton")

        self.outputFolderHorizontalLayout.addWidget(self.outputFolderPushButton)

        self.openOutputFolderPushButton = QPushButton(self.centralwidget)
        self.openOutputFolderPushButton.setObjectName(u"openOutputFolderPushButton")

        self.outputFolderHorizontalLayout.addWidget(self.openOutputFolderPushButton)


        self.formLayout.setLayout(1, QFormLayout.SpanningRole, self.outputFolderHorizontalLayout)

        self.optionVerticalLayout = QVBoxLayout()
        self.optionVerticalLayout.setObjectName(u"optionVerticalLayout")
        self.convertImageFormatHorizontalLayout = QHBoxLayout()
        self.convertImageFormatHorizontalLayout.setObjectName(u"convertImageFormatHorizontalLayout")
        self.convertImageFormatCheckBox = QCheckBox(self.centralwidget)
        self.convertImageFormatCheckBox.setObjectName(u"convertImageFormatCheckBox")

        self.convertImageFormatHorizontalLayout.addWidget(self.convertImageFormatCheckBox)

        self.convertImageFormatComboBox = QComboBox(self.centralwidget)
        self.convertImageFormatComboBox.addItem("")
        self.convertImageFormatComboBox.addItem("")
        self.convertImageFormatComboBox.addItem("")
        self.convertImageFormatComboBox.setObjectName(u"convertImageFormatComboBox")

        self.convertImageFormatHorizontalLayout.addWidget(self.convertImageFormatComboBox)


        self.optionVerticalLayout.addLayout(self.convertImageFormatHorizontalLayout)

        self.compressImageHorizontalLayout = QHBoxLayout()
        self.compressImageHorizontalLayout.setObjectName(u"compressImageHorizontalLayout")
        self.compressImageCheckBox = QCheckBox(self.centralwidget)
        self.compressImageCheckBox.setObjectName(u"compressImageCheckBox")

        self.compressImageHorizontalLayout.addWidget(self.compressImageCheckBox)

        self.compressImageDoubleSpinBox = QDoubleSpinBox(self.centralwidget)
        self.compressImageDoubleSpinBox.setObjectName(u"compressImageDoubleSpinBox")
        self.compressImageDoubleSpinBox.setMaximum(999999.989999999990687)

        self.compressImageHorizontalLayout.addWidget(self.compressImageDoubleSpinBox)

        self.compressImageLabel = QLabel(self.centralwidget)
        self.compressImageLabel.setObjectName(u"compressImageLabel")

        self.compressImageHorizontalLayout.addWidget(self.compressImageLabel)


        self.optionVerticalLayout.addLayout(self.compressImageHorizontalLayout)

        self.renameImageHorizontalLayout = QHBoxLayout()
        self.renameImageHorizontalLayout.setObjectName(u"renameImageHorizontalLayout")
        self.renameImageCheckBox = QCheckBox(self.centralwidget)
        self.renameImageCheckBox.setObjectName(u"renameImageCheckBox")

        self.renameImageHorizontalLayout.addWidget(self.renameImageCheckBox)

        self.renameImageComboBox = QComboBox(self.centralwidget)
        self.renameImageComboBox.addItem("")
        self.renameImageComboBox.addItem("")
        self.renameImageComboBox.addItem("")
        self.renameImageComboBox.setObjectName(u"renameImageComboBox")

        self.renameImageHorizontalLayout.addWidget(self.renameImageComboBox)


        self.optionVerticalLayout.addLayout(self.renameImageHorizontalLayout)

        self.startProcessingPushButton = QPushButton(self.centralwidget)
        self.startProcessingPushButton.setObjectName(u"startProcessingPushButton")

        self.optionVerticalLayout.addWidget(self.startProcessingPushButton)


        self.formLayout.setLayout(2, QFormLayout.LabelRole, self.optionVerticalLayout)

        self.outputInfoVerticalLayout = QVBoxLayout()
        self.outputInfoVerticalLayout.setObjectName(u"outputInfoVerticalLayout")
        self.consoleTextEdit = QTextEdit(self.centralwidget)
        self.consoleTextEdit.setObjectName(u"consoleTextEdit")

        self.outputInfoVerticalLayout.addWidget(self.consoleTextEdit)

        self.totalProgressHorizontalLayout = QHBoxLayout()
        self.totalProgressHorizontalLayout.setObjectName(u"totalProgressHorizontalLayout")
        self.totalProgresslabel = QLabel(self.centralwidget)
        self.totalProgresslabel.setObjectName(u"totalProgresslabel")

        self.totalProgressHorizontalLayout.addWidget(self.totalProgresslabel)

        self.totalProgressBar = QProgressBar(self.centralwidget)
        self.totalProgressBar.setObjectName(u"totalProgressBar")
        self.totalProgressBar.setValue(0)

        self.totalProgressHorizontalLayout.addWidget(self.totalProgressBar)


        self.outputInfoVerticalLayout.addLayout(self.totalProgressHorizontalLayout)


        self.formLayout.setLayout(2, QFormLayout.FieldRole, self.outputInfoVerticalLayout)

        toolBoxMainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(toolBoxMainWindow)
        self.statusbar.setObjectName(u"statusbar")
        toolBoxMainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(toolBoxMainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 825, 22))
        self.menuBar.setAutoFillBackground(False)
        self.menu = QMenu(self.menuBar)
        self.menu.setObjectName(u"menu")
        toolBoxMainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menu.menuAction())
        self.menu.addAction(self.actionAbout)

        self.retranslateUi(toolBoxMainWindow)

        QMetaObject.connectSlotsByName(toolBoxMainWindow)
    # setupUi

    def retranslateUi(self, toolBoxMainWindow):
        toolBoxMainWindow.setWindowTitle(QCoreApplication.translate("toolBoxMainWindow", u"\u56fe\u7247\u5de5\u5177\u7bb1", None))
        self.actionAbout.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u5173\u4e8e", None))
        self.inputFolderlabel.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u8f93\u5165\u6587\u4ef6\u5939", None))
        self.inputFolderPushButton.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u9009\u62e9\u6587\u4ef6\u5939", None))
        self.recursiveloadingCheckBox.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u9012\u5f52\u8f7d\u5165", None))
        self.outputFolderlabel.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u8f93\u51fa\u6587\u4ef6\u5939", None))
        self.outputFolderPushButton.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u9009\u62e9\u6587\u4ef6\u5939", None))
        self.openOutputFolderPushButton.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u5728\u8d44\u6e90\u7ba1\u7406\u5668\u4e2d\u6253\u5f00\u6587\u4ef6\u5939", None))
        self.convertImageFormatCheckBox.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u8f6c\u5316\u56fe\u7247\u683c\u5f0f", None))
        self.convertImageFormatComboBox.setItemText(0, QCoreApplication.translate("toolBoxMainWindow", u"jpeg", None))
        self.convertImageFormatComboBox.setItemText(1, QCoreApplication.translate("toolBoxMainWindow", u"png", None))
        self.convertImageFormatComboBox.setItemText(2, QCoreApplication.translate("toolBoxMainWindow", u"webp", None))

        self.compressImageCheckBox.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u538b\u7f29\u56fe\u7247", None))
        self.compressImageLabel.setText(QCoreApplication.translate("toolBoxMainWindow", u"KB", None))
        self.renameImageCheckBox.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u91cd\u547d\u540d\u56fe\u7247", None))
        self.renameImageComboBox.setItemText(0, QCoreApplication.translate("toolBoxMainWindow", u"uuid", None))
        self.renameImageComboBox.setItemText(1, QCoreApplication.translate("toolBoxMainWindow", u"md5", None))
        self.renameImageComboBox.setItemText(2, QCoreApplication.translate("toolBoxMainWindow", u"auto-increment number", None))

        self.startProcessingPushButton.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u5f00\u59cb", None))
        self.totalProgresslabel.setText(QCoreApplication.translate("toolBoxMainWindow", u"\u603b\u8fdb\u5ea6", None))
        self.menu.setTitle(QCoreApplication.translate("toolBoxMainWindow", u"\u5e2e\u52a9", None))
    # retranslateUi

