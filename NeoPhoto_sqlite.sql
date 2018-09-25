CREATE TABLE "AlbumFolders" ("AlbumsPath" VARCHAR not null, "Description" VARCHAR null, "AlbumID" int not null, foreign key (AlbumID) references Albums(rowid));
CREATE TABLE "AlbumImages" ("Target" INTEGER NOT NULL , "Description" VARCHAR, "AlbumId" INTEGER NOT NULL , "PrevId" INTEGER, foreign key(Target) references Images(rowid),
foreign key(PrevId) references AlbumImages(rowid),
foreign key(AlbumId) references Albums(rowid));
CREATE TABLE "Albums" ("Designation" VARCHAR,"Description" VARCHAR,"created_at" DATETIME DEFAULT (datetime('now')) );
CREATE TABLE "DefaultParamValues" ("RAWfolder" INTEGER,"ImageFolder" INTEGER,"AlbymFolder" INTEGER,"DefaultThumbnailSizeX" INTEGER,"DefaultZhumbnailSizeY" INTEGER DEFAULT (null) );
CREATE TABLE "ImageExts" ("ImageExt" VARCHAR, "Description" VARCHAR, "Class" INTEGER);
CREATE TABLE "ImageFolders" ("FolderPath" VARCHAR not null,"Description" VARCHAR not null, "Class" INTEGER not null);
CREATE TABLE "ImageParents" ("ImageId" INTEGER not null, "ParentId" INTEGER not null
, foreign key (ImageId) references  Images(rowid)
, foreign key (ParentId) references  Images(rowid));
CREATE TABLE "Images" ("file" VARCHAR not null, "FolderID" INTEGER not null, "SubPath" VARCHAR null
,"saved_at" DATETIME DEFAULT (null),"State" INTEGER not null DEFAULT(0)
,foreign key (FolderID) references ImageFolders(rowid));
CREATE TABLE "thumbnails" ("id" INTEGER PRIMARY KEY  NOT NULL  UNIQUE , "thumb" BLOB, foreign key (id) references  Images(rowid)) without ROWID





;
CREATE VIEW "Images_view" AS  SELECT a.rowid,a.file,a.Folderid,a.SubPath,a.saved_at,a.State,b.FolderPath  FROM Images a join ImageFolders b on a.FolderId=b.rowid;
CREATE TRIGGER delete_AlbumImage before delete on AlbumImages
begin
     update AlbumImages set PrevId=OLD.PrevId where PrevId=OLD.rowid;
end;
CREATE TRIGGER insert_AlbumImage after insert on AlbumImages
begin
     update AlbumImages set PrevId=New.rowid where rowid<>NEW.rowid and PrevId is null and New.PrevId is null;
     update AlbumImages set PrevId=NEW.rowid  where PrevId=NEW.PrevId and rowid <> NEW.rowid and NEW.PrevId is not null;
end;
