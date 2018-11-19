
class FileExists(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class FileCache():

    def __init__(self):
        self.files = {}
    
    def addFile(self,tagList,fileName):
        """ добавлет файл в файловый кэш, не проверяя наличия, для этого есть
        соответствующий метод """

        for t in tagList:
            if t['tagType'] not in self.files.keys():
                self.files[t['tagType']] = {}
            if t['tagVal'] not in self.files[t['tagType']].keys():
                self.files[t['tagType']][t['tagVal']] = set()                
            self.files[t['tagType']][t['tagVal']].add(fileName)
            
    def checkFile(self,tagList,fileName):
        """ проверяет наличие файла в файловом кэше,
        возвращает True или False """

        for t in tagList:
            if t['tagType'] not in self.files.keys():
                return False
            if t['tagVal'] not in self.files[t['tagType']].keys():
                return False
            if fileName not in self.files[t['tagType']][t['tagVal']]:
                return False

        return True
