
import os
import sys
import errno

class PhotoFS():
    def __init__(self, root):
        self.root = root

        # тэги
        self.dTag = "tag"	# тип тэга, который можно не указывать
        self.tagTypes = [ "people","year","month","day","geo", self.dTag ] # известные типы тэгов
        self.tags = {}
        for tt in self.tagTypes:
            self.tags[tt] = []
        # кэши (они хранятся в перманентной памяти)
        self.tagCache = {}
        # файлы
        self.stFd = 1000	# номер первого дескриптора файлов
        self.fdList = []	# дескрипторы открытых файлов
        self.stNode = 1		# номер первого файлового узла
        self.fdNodes = {}	# собственно файлы

    # Helpers
    # =======

    def _parse_path(self,path):
        """ парсит путь в список словарей { tagType, tagVal }
        применимо только для путей (не для имен файлов)
        не позволяет создать новый тип тэгов (непонятно - хорошо ли это разрешать...)
        """

        res = []
        if path.startswith("/"):
            path = path[1:]
        for t in path.split('/'):
            if len(t)==0 or t==".." :	# пропускаем всякий мусор ??? а может ли такое быть в жизни
                continue
            tType = self.dTag
            tVal = t
            if t.find('.')>=0:	# предполагаем, что задан тип тэга
                tType,tVal = t.split('.',1)
                if not tType or tType not in self.tagTypes:	# пустой или неправильный тип тэга
                    raise OSError(errno.ENOTDIR,"not such directory")
            newEl = { 'tagType': tType, 'tagVal': tVal }
            if newEl not in res:
                res.append(newEl)
                    
        return res

    def _check_tag(self,tag):
        """ проверяет наличие тэга в списке тэгов файловой системы, 
        возвращает False, если такого тэга нет """

        return tag['tagType'] in self.tags.keys() and tag['tagVal'] in self.tags[tag['tagType']]

    def _check_tag_type (self,tagType):
        """ проверяет наличие тэга в списке типов тэгов файловой системы, 
        возвращает False, если такого типа нет """

        return tagType in self.tagTypes
    
    def _add_tag(self,tag):
        """ добавляет тэг в список тэгов файловой системы, 
        возвращает False, если такой тэг уже есть ИЛИ задан плохой тип тэга """

        if not self._check_tag_type(tag['tagType']):	# такого типа нету...
            return False

        if self._check_tag(tag):	# такой уже есть
            return False

        self.tags[tag['tagType']].append(tag['tagVal'])
        return True
    
    
    # Filesystem methods
    # ==================

    def mkdir(self, path, mode):
        """ создает заданный в пути последоветельность тэгов (
        поведение НЕ аналогично стандартному mkdir, который не создает вложенных директорий)
        mode - нам не нужен, его игнорируем """

        tl = self._parse_path(path)
        isNew = False
        for t in tl:
            if not self._check_tag(t):
                self._add_tag(t)
                isNew = True

        if not isNew:
            raise OSError(errno.EEXIST,"direcory exists")

    def access(self, path, mode):
        """ проверяет доступность пути (файла или директории), возвращает True или False
        Поскольку в нашей файловой системе права доступа отсутствуют - mode игнорируем """

        # сначала проверим - вдруг путь - директория
        isDir = True
        tl = self._parse_path(path)
        for i,t in enumerate(tl):
            if not self._check_tag(t):	# может быть файлом, как быть?
                isDir = False
                break

        if isDir:
            return True

        if i<>len(tl): # задали неверную директорию в середине пути
            return False
        
        # тогда есть вариант, что это - файл, проверим по дескрипторам
        fList = _get_file_descrs(tl[:-1])
        for fd in fList:
            if self.fdNodes[fd]["extName"]==tl[-1]
                raise OSError(errno.EACCES,"no access") # непонятно, почему эксепшн, может быть просто False (взял реакцию в виде эксепшна из примера)

        # надо здесь завязаться с проверкой файлов по кэшу: если мы все нашли (выше), то ок
        # если не все нашли, то, возможно, это имя файла (существующего), его надо поискать по имени в кэше
        # если не нашли - ошибка
        # если нашли - надо проверить тэги (все ли ок), если не ок - ошибка

        return True
    
# дальше не трогал пока ---------------------------------------

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)


    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(name), self._full_path(target))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        """ открытие файла, создание его при открытии на запись """

        dName,fName = os.path.split(path)
        if self.access(dName,1):	# путь задан корректно (иначе будет эксепшн !!!)
            # создаем или перезаписываем файл, пишем его в дескрипторы
            # при создании мы ничего не знаем про EXIF, поэтому пишем все в спул, потом демон должен разгрести
            # и мы не можем создавать новый файл нигде, кроме спула (т.е. без тэгов)
            # проверять на наличие файла мы должны по кэшу (сравнив еще и наличие тэгов в пути и в кэшах)
            # именно это и должна делать функция access() - если файл действительно есть, то просто открыть его
            # иначе - вернуть ошибку
            try:
                fd = os.open(os.path.join(self.root,self.fPool,fName),os.O_WRONLY | os.O_CREAT)
            except:
                raise OSError(errno.EACCES,"no such file")
            # тэговый кэш не меняется при открытии и создании, только при rename()
            # заполняем файловый кэш и таблицу дескрипторов
            self.fNodes.append(fd)
            self.fileCache[fName] = {}	# по файлу также нет тэгов
            return fd

    def create(self, path, mode, fi=None):
        """ создает файл, по сути вызов open() с предопределенным mode """
        return self.open(path, os.O_WRONLY | os.O_CREAT)

# дальше не трогал пока ---------------------------------------

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
