# -*- encoding utf-8 -*-
from ImageAlbums  import ImageAlbums


AlbIm = ImageAlbums('NeoPhoto.sqlite')


NewName ="MyPortrets"
AlbIm.lsAlbumItems(NewName)
print(AlbIm.getRows(NewName,2631))
print(AlbIm.getRow(NewName,4))
"""
AlbIm.appendImage(NewName,2630,'Test1')
AlbIm.appendImage(NewName,2631,'Test2')
AlbIm.appendImage(NewName,2632,'Test3')
print(AlbIm.getRowid(NewName,2632))
#AlbIm.deleteElement(NewName,4)
AlbIm.lsAlbumItems(NewName)
#AlbIm.deleteImageByImageId(NewName,2632)
#AlbIm.lsAlbumItems(NewName)
"""
#desig = "Selfy"
#except Exception as e:
#   print("Ошибка  " + str(e))