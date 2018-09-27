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

class ImagesBlob(QtWidgets.QMainWindow):
    def __init__(self, BaseName):
        super().__init__()

        # Set up the user interface from Designer.
        uic.loadUi("pictureFromBase.ui", self)

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
        self.modelImages.setQuery(s)
        #self.modelFolders.sel
        # self.tableViewFolders.setSelectionBehavior(self.tableViewFolders.SelectRows)
        self.tableViewImages.setModel(self.modelImages)
        smodel = self.tableViewImages.selectionModel()
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
            print(w,h)
            result = qImage.scaled(w, h)
            self.labelThumb.setPixmap(QtGui.QPixmap.fromImage(qImage))
            #self.labelThumb.setAlignment(QtGui.AlignCenter)





app = QtWidgets.QApplication(sys.argv)
BlobForm = ImagesBlob('NeoPhoto.sqlite')

BlobForm.show()
sys.exit(app.exec_())