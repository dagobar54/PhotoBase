# -*- encoding: utf-8 -*-
"""
Поиск способов отобразить картинку из Blob
"""
import os
import sqlite3 as lite
import sys
from datetime import datetime
import time
#import PIL
from io import BytesIO
#from PIL import Image, ImageDraw
import io
from PyQt5 import QtCore, QtWidgets, QtGui, QtSql, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ImageDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0:
            # Получение ссылки на изображение в иконке, если его нет, тогда вызывается родительский метод рисования
            index = index.model().index(index.row(), 7)
            imgBytes = index.model().data(index)
            if imgBytes is None:
                super().paint(painter, option, index)
                return
            qImage = QtGui.QImage()
            qImage.loadFromData(imgBytes)
            # Получение размеров ячейки и растягивание иконки на размер ячейки
            rect = option.rect
            if qImage.width() >qImage.height():
                w = min(rect.size().width(), qImage.width())
                h = int(w / qImage.width() * qImage.height())

            else:
                h = min(rect.size().height()-50, qImage.height())
                w = int(h / qImage.height() * qImage.width())
            left = rect.left() + (rect.width() - qImage.width()) // 2
            top = rect.top() + (rect.height()-50 - qImage.height()) // 2
            #print(rect,left,top)
            rectImage=QtCore.QRect(left,top,w,h)
            #print(rect)
            #img = qImage.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            painter.save()
            if option.state & QStyle.State_Selected:
                painter.setBrush(QtGui.QBrush(Qt.blue))
                painter.setPen(QPen(Qt.yellow, 1, Qt.SolidLine))
            else:
                painter.setBrush(QtGui.QBrush(Qt.gray))
                painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
            rectFrame = QtCore.QRect(rect.left() + 2, rect.top() + 2, rect.width() - 4, rect.height()-4)
            painter.drawRect(rectFrame)
            ind = index.model().index(index.row(), 1)
            imgFileName = index.model().data(ind)
            rectText = QtCore.QRect(rect.left()+2, rect.top()+rect.height()-50, rect.width()-4, 45)
            font =QFont("Arial", 10);
            font.setBold(True);
            #font.setItalic(True);
            painter.setFont(font);
            #painter.setFont(QFont('Decorative', 12))
            painter.drawText(rectText, Qt.AlignCenter | Qt.TextWordWrap, imgFileName)
            painter.restore()

            painter.drawPixmap(rectImage, QtGui.QPixmap.fromImage(qImage,Qt.NoFormatConversion))

            item_option = QtWidgets.QStyleOptionViewItem(option)

        else:
            QtWidgets.QStyledItemDelegate.paint(self,painter,option,index)

        # Если хотим что-то дорисовать (например текст)
        # super().paint(painter, option, index)
    def sizeHint(self,option,index):
        if index.column() == 0:
            return QtCore.QSize(220,250)
        else:
            newsize = QtWidgets.QStyledItemDelegate.sizeHint(self, option, index)
            print(newsize)
            return newsize

class ImagesList(QtWidgets.QMainWindow):
    def __init__(self, BaseName):
        super().__init__()

        # Set up the user interface from Designer.
        uic.loadUi("pictureListBase.ui", self)

        # self._conn = lite.connect(BaseName)
        # self._cur=self._conn.cursor()

        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(BaseName)
        ok = self.db.open()
        if not ok:
            print("Invalid Database")
            return

        self._conn = lite.connect(BaseName)
        self._cur = self._conn.cursor()

        s = 'select DefaultThumbnailSizeX,DefaultThumbnailSizeY from DefaultParamValues'
        row = self._cur.execute(s).fetchone()
        self._width = int(row[0])
        self._height = int(row[1])

        s = "SELECT rowid,file,Folderid,SubPath,saved_at,State,FolderPath,thumb  FROM images_View where state = 0 and FolderId=3"
        q = QtSql.QSqlQuery()
        q.exec(s)
        self.modelImages = QtSql.QSqlQueryModel()
        self.modelImages.setQuery(q)
        self.listViewImages.setModel(self.modelImages)
        #self.listViewImages.verticalHeader().setDefaultSectionSize(self._height);
        #self.tableViewImages.horizontalHeader().setDefaultSectionSize(self._width);
        id = ImageDelegate()
        self.listViewImages.setItemDelegate(id)
        smodel = self.listViewImages.selectionModel()
        smodel.currentRowChanged.connect(self.folder_row_changed)

    def folder_row_changed(self, newRowId, oldRowId):
        #print(oldRowId.row(), newRowId.row())
        if newRowId.row() > 0:
            ind = int(newRowId.row())
            #index = QtCore.QModelIndex()
            index =self.modelImages.index(ind, 7)

            picArray = self.modelImages.data(index)#.value()#.toByteArray() #record(ind).field("thumb").value().toByteArray()
            qImage = QtGui.QImage()
            qImage.loadFromData(picArray)
            w = qImage.width()
            h = qImage.height()
            #print(w,h)
            result = qImage.scaled(w, h)
            self.labelThumb.setPixmap(QtGui.QPixmap.fromImage(qImage))
            #self.labelThumb.setAlignment(QtGui.AlignCenter)





app = QtWidgets.QApplication(sys.argv)
BlobForm = ImagesList('NeoPhoto.sqlite')

BlobForm.show()
sys.exit(app.exec_())