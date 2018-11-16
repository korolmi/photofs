import pytest
import errno
import os
import subprocess
import glob

import photofs as phfs

@pytest.fixture(scope="function")
def fs():
    """ стандартный setup и teardown для всех тестов """

    yield phfs.PhotoFS("/tmp")
    # teardown
    files = glob.glob("/tmp/fpool/*")
    for f in files:
        os.remove(f)
    
def test_open_smoke_newfile(fs):

    fp = fs.open("photo.jpg",os.O_WRONLY)
    
    assert len(fs.fNodes) == 1
    assert fs.fNodes[0] == fp
    assert os.access(os.path.join(fs.root,fs.fPool,"photo.jpg"),os.R_OK) == True
    assert fs.fileCache["photo.jpg"] == {}	# нет тэгов
