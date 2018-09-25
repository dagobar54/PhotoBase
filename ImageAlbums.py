# -*- encoding utf-8 -*-
"""
Работа с альбомами в базе PhotoWorld
"""
import os
import sqlite3 as lite
import sys
from datetime import datetime
import time
import PIL
from PIL import Image
import io

class ImageAlbums:
    def __init__(self,BaseName):
        self._conn = lite.connect(BaseName)
        self._cur=self._conn.cursor()
        s="select rowid from Albums where Designation = ?"
        album_rows = self._cur.execute(s,("Se",))
        
    def createAlbum(self,AlbumName,AlbumDescription):
        try:
            s = "insert into Albums (Designation,Description)values(?,?)"
            self._cur.execute(s,(AlbumName,AlbumDescription))
            #raise Exception("При попытке вставить альбом [{}]-{}".format(AlbumName,AlbumDescription))
            self._conn.commit()
            print("Created album [%s]",(AlbumName,))
        except Exception as e:
            self._conn.rollback()
            raise Exception("При попытке вставить альбом [{}]\r\n{}".format(AlbumName,str(e)))
            #raise Exception(e)

    
    def renameAlbum(self,OldAlbum,AlbumName,AlbumDescriptor):
        oldId = self.getAlbumId(OldAlbum)
        try:
            if AlbumDescriptor == None:
                s = "update Albums set Designation=? where rowid=?"
                self._cur.execute(s,(AlbumName,oldId))
            else:
                s = "update Albums set Designation=?,Description=? where rowid=?"
                self._cur.execute(s,(AlbumName,AlbumDescriptor,oldId))
            self._conn.commit()
            print("Album [%s] renamed to [%s]",(OldAlbum,AlbumName,))
        except Exception as e:
            raise Exception(e)

    def deleteAlbum(self,AlbumName):
        try:
            albumId = self.getAlbumId(AlbumName)
            s = "delete from AlbumImages where AlbumId=?"
            self._cur.execute(s,(albumId,))
            
            s = "delete from Albums where rowid=?"
            self._cur.execute(s,(albumId,))
            self._conn.commit()
            print("Album [%s] was deleted from base",(AlbumName,))
        except Exception as e:
            raise Exception(e)

    def lsAlbumItems(self,AlbumName):
        try:
            albumId = self.getAlbumId(AlbumName)
            s = "select rowid,Target,PrevID from AlbumImages where AlbumId = ?"
            imageList =  self._cur.execute(s,(albumId,)).fetchall()
            aList = []
            if len(imageList) == 0:
                print("Album is empty")
            else:
                #print(imageList)
                num =[index for (index, consist) in enumerate(imageList) if consist[2] == None][0]
                #print(num)
                while not num is None:
                    imageId = imageList[num][1]
                    aList.append(imageId)
                    nextId = imageList[num][0]
                    nextImage =[index for (index, consist) in enumerate(imageList) if consist[2] == nextId]
                    if nextImage == []:
                        num = None
                    else:
                        num = nextImage[0]
                    #print(num)
                print(aList)
            return aList       
        except Exception as e:
            raise Exception("При попытке получить список состава альбома [{}]".format(AlbumName))
  
    def appendImage(self,AlbumName,ImageId,Description):
        try:
            albumId = self.getAlbumId(AlbumName)
            s = "select a.rowid from AlbumImages a left outer join AlbumImages b on "\
                +"a.rowid=b.PrevId where a.AlbumId = ? and b.Target is null"
            image_row = self._cur.execute(s,(albumId,)).fetchone()
            #print(image_row)
            if image_row is None:
                s = "insert into AlbumImages (AlbumId,Target,Description)values(?,?,?)"
                self._cur.execute(s,(albumId,ImageId,Description))
            else:
                prev = int(image_row[0])
                s = "insert into AlbumImages (AlbumId,Target,Description,PrevId)values(?,?,?,?)"
                self._cur.execute(s,(albumId,ImageId,Description,prev))
            self._conn.commit()    
        except Exception as e:
            raise Exception(e)

    def insertImageAfter(self,AlbumName,afterId,ImageId,Description):
        try:
            albumId = self.getAlbumId(AlbumName)
            s = "select a.rowid,a.PrevId from AlbumImages a where a.AlbumId = ? and a.rowid = ?"
            image_row = self._cur.execute(s,(albumId,afterId)).fetchone()
            #print(image_row)
            if image_row is None:
                raise Exception("Нет элемента альбома с индексом {}".format(afterId,))
            else:
                s = "insert into AlbumImages (AlbumId,Target,Description,PrevId)values(?,?,?,?)"
                self._cur.execute(s,(albumId,ImageId,Description,afterId))               
            self._conn.commit()    
        except Exception as e:
            raise Exception(e)
        
    def insertImageBefore(self,AlbumName,beforeId,ImageId,Description):
        try:
            albumId = self.getAlbumId(AlbumName)
            s = "select a.rowid,a.PrevId from AlbumImages a where a.AlbumId = ? and a.rowid = ?"
            image_row = self._cur.execute(s,(albumId,beforeId)).fetchone()
            #print(image_row)
            if image_row is None:
                raise Exception("Нет элемента альбома с индексом {}".format(beforeId,))
            else:
                prev = int(image_row[1])
                self.insertImageAfter(AlbumName,prev,ImageId,Description)
                
        except Exception as e:
            raise Exception(e)
        
    def changeElementPosition(self,AlbumName,elementId,afterId):
         try:
            albumId = self.getAlbumId(AlbumName)
            if elementId==afterId:
                return
            s = "select a.rowid,a.PrevId from AlbumImages a where a.AlbumId = ? and a.rowid = ?"
            image_row = self._cur.execute(s,(albumId,elementId)).fetchone()
            #print(image_row)
            if image_row is None:
                raise Exception("Нет элемента альбома с индексом {}".format(afterId,))
            elif afterId == int(image_row[1]):
                return
            else:
                #Замыкаем следующий на предыдущего от текущего
                prev =int(image_row[1])
                s = "update AlbumImages set PrevId=? where a.AlbumId = ? and a.PrevId = ?"
                self._cur.execute(s,(prev,albumId,elementId)).fetchone() 
                #Следующего после afterId замыкаем на текущего
                s = "update AlbumImages set PrevId=? where a.AlbumId = ? and a.PrevId = ?"
                self._cur.execute(s,(elementId,albumId,afterId)).fetchone()
                #Текущий замыкаем на afterId
                s = "update AlbumImages set PrevId=? where a.AlbumId = ? and a.PrevId = ?"
                self._cur.execute(s,(afterId,albumId,elementId)).fetchone() 

         except Exception as e:
            raise Exception(e)       

    def deleteImageByImageId(self,AlbumName,ImageId):
        try:
            albumId = self.getAlbumId(AlbumName)
            s = "select a.rowid,a.PrevId from AlbumImages a where a.AlbumId = ? and a.Target = ?"
            image_rows = self._cur.execute(s,(albumId,ImageId)).fetchall()
            if len(image_rows)> 1:
                raise Exception("В альбоме {} ,более одного раза использован элемент {}".
                                format(AlbumName,ImageId))
            
            elif len(image_rows) == 0:
                raise Exception("Нет в альбоме {} изображения с Id={}".format(AlbumName,ImageId))
            else:
                image_row = image_rows[0]
                rowid = int(image_row[0])#удаляемого элемента
                prevId= int(image_row[1])
                s = "delete from AlbumImages where rowid=?"
                self._cur.execute(s,(rowid,))          
            self._conn.commit()    
        except Exception as e:
            raise Exception(e)

    def deleteElement(self,AlbumName,ElementId):
        try:
            albumId = self.getAlbumId(AlbumName)
            s = "select a.rowid,a.PrevId from AlbumImages a where a.AlbumId = ? and a.rowid = ?"
            image_rows = self._cur.execute(s,(albumId,ElementId)).fetchall()
            print(image_rows)
            if len(image_rows) == 0:
                raise Exception("Нет в альбоме {} элемента с Id={}".format(AlbumName,ElementId))
            else:
                self._cur.execute(s,(ElementId,))
            self._conn.commit()    
        except Exception as e:
            raise Exception(e)

    def getRows(self,AlbumName,ImageId):
        """ Получить rows по ImageId"""
        albumId = self.getAlbumId(AlbumName)
        s="select rowid,Target,Description,PrevId from AlbumImages where AlbumId = ? and Target=?"
        album_rows = self._cur.execute(s,(albumId,ImageId)).fetchall()
        if len(album_rows) == 0:
            raise Exception("Альбом [{}] не зарегистрован".format(AlbumName))
        else:
            return album_rows

    def getRow(self,AlbumName,elementId):
        """ Получить row по ElementId"""
        albumId = self.getAlbumId(AlbumName)
        s="select rowid,Target,Description,PrevId from AlbumImages where AlbumId = ? and rowid=?"
        album_rows = self._cur.execute(s,(albumId,elementId)).fetchall()
        if len(album_rows) == 0:
            raise Exception("Альбом [{}] не зарегистрован или элемента {} нет в альбоме".format(AlbumName, elementId))
        else:
            return album_rows

    def getAlbumId(self,AlbumName):
        """ Получить AlbumId"""
        if type(AlbumName)=="int":
            return AlbumName
        else:
            s="select rowid from Albums where Designation = ?"
            album_row = self._cur.execute(s,(AlbumName,)).fetchone()
            #album_row =album_rows.fetchone()
            if album_row == None:
                raise Exception("Альбом [{}] не зарегистрован".format(AlbumName))
            return int(album_row[0])


            
            
