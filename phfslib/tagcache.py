class TagExists(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class BadTagType(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class NoTagType(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
        
class TagCache():

    def __init__(self,types):

        self.tagTypes = types 	# список типов тэгов, с которыми работает кэш
        self.tags = {}		# [тип] = тэг
        for tt in self.tagTypes:
            self.tags[tt] = set()

    def _parseDirPath(self,path):
        """ парсит путь в список словарей { tagType, tagVal }
        применимо только для путей (не для имен файлов)
        не позволяет создать новый тип тэгов (непонятно - хорошо ли это разрешать...)
        райзит
            BadTagType - если задан плохой тип тэга
            NoTagType - если не задан тип тэга
        """

        res = []
        if path.startswith("/"):
            path = path[1:]
        for t in path.split('/'):
            if len(t)==0 or t==".." :	# пропускаем всякий мусор ??? а может ли такое быть в жизни
                continue
            if t.find('.')>=0:	# предполагаем, что задан тип тэга
                tType,tVal = t.split('.',1)
                if not tType or tType not in self.tagTypes:	# пустой или неправильный тип тэга
                    raise BadTagType
            else:
                raise NoTagType
            
            newEl = { 'tagType': tType, 'tagVal': tVal }
            if newEl not in res:
                res.append(newEl)
                    
        return res

    def addDirPath(self,path):
        """ добавляет тэги из пути в список тэгов кэша,
        райзит те же исключения, что и parse(потому что использует)
        не проверяет на наличие - для этого есть другой метод
        по идее сначала надо проверить, что путь существует, потом добавлять """

        tl = self._parseDirPath(path)
        for t in tl:
            self.tags[t['tagType']].add(t['tagVal'])            


    def checkDirPath(self,path):
        """ проверяет наличие тэгов в кэш,
        райзит те же исключения, что и parse(потому что использует)
        возвращает True - путь (комбинация тэгов) существует
        False в противном случае """

        tl = self._parseDirPath(path)
        for t in tl:
            if t['tagVal'] not in self.tags[t['tagType']]:            
                return False
        return True

