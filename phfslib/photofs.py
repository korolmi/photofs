
import os
import sys
import errno

import tagcache as tc


class PhotoFS():
    def __init__(self, root, tcache):
        self.root = root
        self.tagCache = tcache

        # файлы
        self.stFd = 1000	# номер первого дескриптора файлов
        self.fdList = []	# дескрипторы открытых файлов
        self.stNode = 1		# номер первого файлового узла
        self.fdNodes = {}	# собственно файлы
    
    # Filesystem methods
    # ==================

    def mkdir(self, path, mode):
        """ создает заданный в пути последоветельность тэгов (
        поведение НЕ аналогично стандартному mkdir, который не создает вложенных директорий)
        mode - нам не нужен, его игнорируем """

        try:
            if self.tagCache.checkDirPath(path):
                raise OSError(errno.EEXIST,"all tags already exist")
            self.tagCache.addDirPath(path)
        except tc.BadTagType:
            raise OSError(errno.EINVAL,"bad tag type")
        except tc.NoTagType:
            raise OSError(errno.EINVAL,"tag type should be specified")

    def access(self, path, mode):
        """ проверяет доступность пути (файла или директории), возвращает True или False
        Поскольку в нашей файловой системе права доступа отсутствуют - mode игнорируем """

        if self.tagCache.checkDirPath(path):
            return True
        
        if self.fileCache.checkFilePath(path):
            return True

        return False
            
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

