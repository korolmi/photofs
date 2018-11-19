import pytest
import errno
import os
import glob

import storage as st

@pytest.fixture(scope="function")
def sts():
    """ стандартный setup для всех тестов """
    yield st.Storage("/tmp/photofs")
    files = glob.glob('/tmp/photofs/*')
    for f in files:
        os.remove(f)

# ======================================== INIT
def test_init_smoke(sts):

    assert sts.root=="/tmp/photofs"

# ======================================== CREATE_FILE_PATH

def test_createFile_smoke(sts):

    path = sts.createFile('file.jpg')
    assert path.find("file.jpg")>0
    assert os.access(path,os.F_OK)==True 

def test_createFile_dupl(sts):

    path = sts.createFile('file.jpg')
    with pytest.raises(Exception) as ex:
        path = sts.createFile('file.jpg')
    assert ex.value.errno==errno.EEXIST
    
def test_createFile_path(sts):

    with pytest.raises(Exception) as ex:
        path = sts.createFile('/tmp/file.jpg')
    assert ex.value.errno==errno.EINVAL

    with pytest.raises(Exception) as ex:
        path = sts.createFile('dir/file.jpg')
    assert ex.value.errno==errno.EINVAL
    
# =========================================== REMOVE_FILE

def test_removeFile_smoke(sts):

    path = sts.createFile('file.jpg')

    sts.removeFile('file.jpg')
    assert os.access(path,os.F_OK)==False 
