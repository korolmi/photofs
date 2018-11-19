import os
import errno

class NoMoreFiles(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class Storage():

    def __init__(self,root):
        self.root = root

    def _makePath(self,fileName):
        """ создает путь в хранилище, 
        если дать имя файла с любым путем (даже относительным) - райзится EINVAL """

        path,name = os.path.split(fileName)
        if path:
            raise OSError(errno.EINVAL,"cannot create path")

        return os.path.join(self.root,fileName)
        
    def createFile(self,fileName):
        """ создает файл в хранилище,
        если файл существует - райзится ошибка EEXIST
        если не получается создать файл - райзится стандартная ошибка """

        resName = self._makePath(fileName)
        if os.access(resName,os.F_OK):
            raise OSError(errno.EEXIST,"file exists, cannot be overwritten")
        
        fd = open(resName,"w")
            
        fd.close()

        return resName

    def removeFile(self,fileName):
        """ удаляет файл из хранилища,
        если файл не существует - райзится ошибка ENOENT
        если не получается удалить файл - райзится стандартная ошибка """

        resName = self._makePath(fileName)
        if not os.access(resName,os.F_OK):
            raise OSError(errno.ENOENT,"file doe not exist")
        
        os.remove(resName)
    
