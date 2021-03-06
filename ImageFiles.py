from PyQt5 import QtCore, QtWidgets, QtGui, QtSql, uic
import sys
import sqlite3 as lite
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
                painter.setBrush(QtGui.QBrush(Qt.darkGray))
                painter.setPen(QPen(Qt.cyan, 1, Qt.SolidLine))
            else:
                painter.setBrush(QtGui.QBrush(Qt.lightGray))
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


class ImageFiles:
    def __init__(self, BaseName):
        self._conn = lite.connect(BaseName)
        self._cur = self._conn.cursor()

class ImageListModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None, *args):
        super(ImageListModel, self).__init__()
        self.datatable = None

    def update(self, dataIn):
        self.datatable = dataIn

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            return '{0}'.format(self.datatable.iget_value(i, j))
        else:
            return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled



class ImagesForm(QtWidgets.QMainWindow):
    def __init__(self, BaseName):
        super().__init__()

        # Set up the user interface from Designer.
        uic.loadUi("expFiles.ui", self)

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

        s = "select FolderPath,Description,rowid as id from PositiveFolders_View"
        q = QtSql.QSqlQuery()
        q.exec(s)
        self.modelFolders = QtSql.QSqlQueryModel()
        self.modelFolders.setQuery(s)
        #self.modelFolders.sel
        # self.tableViewFolders.setSelectionBehavior(self.tableViewFolders.SelectRows)
        self.tableViewFolders.setModel(self.modelFolders)
        smodel = self.tableViewFolders.selectionModel()
        smodel.currentRowChanged.connect(self.folder_row_changed)


        self.modelSubFolders = QtSql.QSqlQueryModel()
        self.tableViewSubFolders.setModel(self.modelSubFolders)
        self.querySubFolders = QtSql.QSqlQuery(self.db)
        self.tableViewSubFolders.setModel(self.modelSubFolders)
        self.querySubFolders.prepare('select SubPath,cnt,FolderId from SubFolders_View where FolderId = ?')
        #self.refreshSubFolders(1)


        s = "SELECT rowid,file,Folderid,SubPath,saved_at,State,FolderPath,thumb  FROM images_View where state = 0 and FolderId=?"
        self.queryImages = QtSql.QSqlQuery()
        self.queryImages.prepare(s)
        self.modelImages = QtSql.QSqlQueryModel()
        self.modelImages.setQuery(self.queryImages)
        self.listViewImages.setModel(self.modelImages)
        id = ImageDelegate()
        self.listViewImages.setItemDelegate(id)
        smodel = self.listViewImages.selectionModel()
        smodel.currentRowChanged.connect(self.image_index_changed)

    def folder_row_changed(self, newRowId, oldRowId):
        #print(oldRowId.row(), newRowId.row())
        if newRowId.row() >= 0:
            ind = int(newRowId.row())
            id: int = int(self.modelFolders.record(ind).field("id").value())
            #print(id)
            self.refreshSubFolders(id)
            self.refreshImages(id)

    def refreshSubFolders(self, folderId):
        self.querySubFolders.addBindValue(folderId)
        self.querySubFolders.exec_()
        self.modelSubFolders.setQuery(self.querySubFolders)

    def refreshImages(self, folderId):
        self.queryImages.addBindValue(folderId)
        self.queryImages.exec_()
        self.modelImages.setQuery(self.queryImages)

    def image_index_changed(self, newId, oldId):
        print(oldId.row(), newId.row())

app = QtWidgets.QApplication(sys.argv)
ImForm = ImagesForm('NeoPhoto.sqlite')

ImForm.show()
sys.exit(app.exec_())
