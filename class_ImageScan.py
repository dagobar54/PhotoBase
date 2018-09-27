import os
import sqlite3 as lite
import sys
from datetime import datetime
import time
import PIL
from PIL import Image
import io

class ImageScan:
    def __init__(self,exts,IWpath,BaseName,height,width):
        self._conn = lite.connect(BaseName)
        self._cur=self._conn.cursor()
        s = 'select rowid,FolderPath,Class from ImageFolders where FolderPath = ?'
        path_rows  = self._cur.execute(s,(IWpath,))

        path_row =path_rows.fetchone()
        if path_row == None:
            raise Exception("Путь [{}] не зарегистрован в PhotoWorld".format(IWpath))
        self._folderPathId = path_row[0]
        self._IWpath = IWpath
        
        s = 'select ImageExt from ImageExts'
        ext_rows  = self._cur.execute(s).fetchall()
        for ex in exts:
            i = ext_rows.index((ex,))
            if 1 < 0:
                raise ValueError("{} нет в списке раширений".format(ex))
        self._exts =exts
        if height==0 or width==0:
            s = 'select DefaultThumbnailSizeX,DefaultThumbnailSizeY from DefaultParamValues'
            row  = self._cur.execute(s).fetchone()
            self._width =row[0]
            self._height = row[1]
        else:
            self._width =width
            self._height = height

    def StartScan (self,dirPath):
        self.dir_scan(dirPath)
        self._conn.commit()
        self._conn.close()

    def GetSubdir(self,dirPath):
        s = dirPath[len(self._IWpath)+1:]
        print('SubDirPath=',s)
        return s
        
    def dir_scan(self,subdir):
        """Рекурсивная процедура, которая сканирует директорию
            и проверяет требует ли файл регистрации в базе или изинения аттрибутов"""
        path = self._IWpath+"\\"+subdir
        f_cnt = 0
        for f in os.scandir(path):
            #print(f.path)
            fname = f.name
            if f.is_file():
                f_cnt +=1
                #print(extension)
                extension = fname.split('.')[-1].upper()
                if extension in self._exts:
                    stat = os.stat(f.path)
                    sec=int(stat.st_ctime)
                    st = datetime.utcfromtimestamp(sec)
                    #print(subdir,f.name)
                    self.insert_image(subdir,f.name,st)
                    #break
                else:
                    continue
            elif f.is_dir():
                print ("Subdir=",f.path)
                p= self.GetSubdir(f.path)
                self.dir_scan(p)
                
        print("Файлов ",f_cnt)
            
    def resize_thumbnail(self,img):
        if img.size[0]>= img.size[1]:
                ratio = (self._width / float(img.size[0]))
                h = int((float(img.size[1]) * float(ratio)))
                img = img.resize((width, h), PIL.Image.ANTIALIAS)
        else:
                ratio = (self._height / float(img.size[1]))
                w = int((float(img.size[0]) * float(ratio)))
                img = img.resize((w, height), PIL.Image.ANTIALIAS)
                #data = lite.Binary(img)
                
    def insert_thumbnale(self,path,rowid):
        img = Image.open(path)
        self.resize_thumbnail(img)
        output = io.BytesIO()
        img.save(output, format='JPEG')
        hex_data = output.getvalue()
        self._cur.execute('INSERT INTO Thumbnails (id,thumb)VALUES(?,?)',\
                              (rowid,lite.Binary(hex_data)))
            
    def update_thumbnail(self,path,rowid):
        img = Image.open(path)
        self.resize_thumbnail(img)
        output = io.BytesIO()
        img.save(output, format='JPEG')
        hex_data = output.getvalue()
        self._cur.execute('UPDATE Thumbnails set thumb =?)',(rowid,lite.Binary(hex_data),))
        
    def insert_image(self,subdir,fname,saved_at):
        path =self._IWpath+"\\"+subdir+"\\"+fname
        #print (path)
        #print(time.ctime(saved_at))

        rowid = 0 #id записи в базе с файлом 
        s = "select rowid,subpath,FolderPath,file,saved_at from Images_view where FolderPath= \
            ? and subpath= ? and  file= ?"
        #print(s)
        #rows = self._cur.execute(s,{"FolderPath":self._IWpath,"subpath":subdir,"file":fname).fetchall()
        rows = self._cur.execute(s,(self._IWpath,subdir,fname)).fetchall()                         
        #print(rows)

        updateThumb = False    
        if len(rows) == 0:  #если файл новый
                s = "insert into Images (file, FolderID,SubPath,saved_at,State)\
                    values(:file,:FolderId,:SubPath,:saved_at,:state)"
                #s = "insert into Images select '"+fname+"',rowid,'"+subdir+"',,saved_at,State)values(?,?,?,?,?)"
                #print (s)
                self._cur.execute(s,{"file":fname,"FolderId":self._folderPathId,"SubPath":subdir,"saved_at":saved_at,"state":0})
                oldrows =self._cur.execute('select last_insert_rowid()')
                rowid =oldrows.fetchone()[0]
                updateThumb = True
                #print('Новый image rowid=',rowid)
        else:
                row = rows[0]
                rowid=row[0]
                #print(row[4],str(saved_at))
                if str(row[4]) != str(saved_at): #файл был изменен
                    updateThumb = True  #flag изменения иконки
                    s = "update Images set saved_at=? where rowid=?"
                    #print (s)
                    self._cur.execute(s,(saved_at,rowid))
                    #print (row)
                rowid=0
        s = 'select id from thumbnails where id= ?'
        th_rows  = self._cur.execute(s,(rowid,))

        th_row =th_rows.fetchone()
        if th_row == None:
            print('Занести пропущенный '+str(rowid)+'  '+path)
            self.insert_thumbnale(path,rowid)

        elif updateThumb:
            print('Обновить thumbnail для rowid= ',rowid,'  ',path+"\\"+fname)
            self.update_thumbnale(path,rowid)



ext =['JPG','PCX','TIF']
width = 200
height=150
#try:
imscan = ImageScan(ext,"I:\\Photo\\bayandin",'NeoPhoto.sqlite',height,width)

imscan.StartScan("")
#except Exception as e:
#   print("Ошибка  " + str(e))
    
    

