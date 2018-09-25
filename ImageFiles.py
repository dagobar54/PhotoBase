from PyQt5 import QtCore, QtWidgets, QtGui, QtSql, uic
import sys
import sqlite3 as lite


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


class ImageDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Получение ссылки на изображение в иконке, если его нет, тогда вызывается родительский метод рисования
        img = index.model().data(index, QtCore.Qt.DecorationRole)
        if img is None:
            super().paint(painter, option, index)
            return

        # Получение размеров ячейки и растягивание иконки на размер ячейки
        rect = option.rect
        w, h = rect.size().width(), rect.size().height()
        img = img.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        painter.drawPixmap(rect, img)

        item_option = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(item_option, index)

        # Обработка при выделении ячейки делегата
        # Рисуем выделение полупрозрачным чтобы было видно нарисованное ранее
        if item_option.state & QtWidgets.QStyle.State_Selected:
            # Получаем цвет, используемый при выделении ячеек
            color = item_option.palette.color(QtWidgets.QPalette.Highlight)

            # Делаем его полупрозрачным
            color.setAlpha(180)

            # Сохранение состояния рисовальщика, изменение состояния, рисование и восстановление старого состояния
            painter.save()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(rect)
            painter.restore()

        # Если хотим что-то дорисовать (например текст)
        # super().paint(painter, option, index)

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
        s = "select FolderPath,Description,rowid as id from PositiveFolders_View"
        q = QtSql.QSqlQuery()
        q.exec(s)
        self.modelFolders = QtSql.QSqlQueryModel()
        self.modelFolders.setQuery(s)
        # self.tableViewFolders.setSelectionBehavior(self.tableViewFolders.SelectRows)
        self.tableViewFolders.setModel(self.modelFolders)
        smodel = self.tableViewFolders.selectionModel()


        self.modelSubFolders = QtSql.QSqlQueryModel()
        self.tableViewSubFolders.setModel(self.modelSubFolders)
        self.querySubFolders = QtSql.QSqlQuery(self.db)
        self.tableViewSubFolders.setModel(self.modelSubFolders)
        self.querySubFolders.prepare('select SubPath,cnt,FolderId from SubFolders_View where FolderId = ?')
        #self.refreshSubFolders(1)
        smodel.currentRowChanged.connect(self.folder_row_changed)

        self.itemImagesModel = QtSql.QSqlQueryModel()
        self.queryImages = QtSql.QSqlQuery(self.db)

        self.queryImages.prepare(' SELECT rowid,file,Folderid,SubPath,saved_at,State,FolderPath,thumb  FROM images_View where state = 0 and FolderId = ?')
        self.listViewImages.setModel(self.itemImagesModel)
        delegate = ImageDelegate()
        self.listViewImages.setItemDelegate(delegate)

    def folder_row_changed(self, newRowId, oldRowId):
        print(oldRowId.row(), newRowId.row())
        if newRowId.row() >= 0:
            ind = int(newRowId.row())
            id: int = int(self.modelFolders.record(ind).field("id").value())
            #print(id)
            self.refreshSubFolders(id)

    def refreshSubFolders(self, folderId):
        self.querySubFolders.addBindValue(folderId)
        self.querySubFolders.exec_()
        self.modelSubFolders.setQuery(self.querySubFolders)

        self.queryImages.addBindValue(folderId)
        self.queryImages.exec_()
        self.itemImagesModel.setQuery(self.queryImages)

app = QtWidgets.QApplication(sys.argv)
ImForm = ImagesForm('NeoPhoto.sqlite')

ImForm.show()
sys.exit(app.exec_())
