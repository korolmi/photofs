import pytest
import errno

import filecache as fc

@pytest.fixture
def stc():
    """ стандартный setup для всех тестов """
    return fc.FileCache()

# ======================================== INIT
def test_init_smoke(stc):

    pass

# ======================================== ADD_FILE_PATH

def test_addFile_smoke(stc):

    stc.addFile([{'tagType':'people','tagVal':'mike'}],'file.jpg')

    assert "file.jpg" in stc.files["people"]["mike"]

def test_addFile_real(stc):

    stc.addFile([
        {'tagType':'people','tagVal':'mike'},
        {'tagType':'year','tagVal':'2018'}],
        'file.jpg')

    assert "file.jpg" in stc.files["people"]["mike"]
    assert "file.jpg" in stc.files["year"]["2018"]

def test_addFile_order(stc):

    stc.addFile([
        {'tagType':'year','tagVal':'2018'},
        {'tagType':'people','tagVal':'mike'}],
        'file.jpg')

    assert "file.jpg" in stc.files["people"]["mike"]
    assert "file.jpg" in stc.files["year"]["2018"]
    
def test_addFile_dupl(stc):

    stc.addFile([{'tagType':'people','tagVal':'mike'}],'file.jpg')
    stc.addFile([{'tagType':'people','tagVal':'mike'}],'file.jpg')

    assert "file.jpg" in stc.files["people"]["mike"]
    
# ======================================== CHECK_FILE_PATH

def test_checkFile_smoke(stc):

    assert stc.checkFile([{'tagType':'people','tagVal':'mike'}],'file.jpg')==False
    stc.addFile([{'tagType':'people','tagVal':'mike'}],'file.jpg')
    assert stc.checkFile([{'tagType':'people','tagVal':'mike'}],'file.jpg')==True

def test_checkFile_real(stc):

    stc.checkFile([
        {'tagType':'year','tagVal':'2018'},
        {'tagType':'people','tagVal':'mike'}],
        'file.jpg') == False
    stc.addFile([
        {'tagType':'year','tagVal':'2018'},
        {'tagType':'people','tagVal':'mike'}],
        'file.jpg')
    stc.checkFile([
        {'tagType':'year','tagVal':'2018'},
        {'tagType':'people','tagVal':'mike'}],
        'file.jpg') == True
    
    
