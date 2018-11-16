import pytest
import errno

import photofs as phfs

@pytest.fixture
def fs():
    """ стандартный setup для всех тестов """

    return phfs.PhotoFS("/tmp")

def test_init_smoke(fs):

    assert fs.root == "/tmp"
    assert fs.dTag == "tag"
    assert "people" in fs.tagTypes
    assert "year" in fs.tagTypes
    assert "month" in fs.tagTypes
    assert "day" in fs.tagTypes
    assert "geo" in fs.tagTypes
    assert "tag" in fs.tagTypes
    
# =========================================== PARSE_PATH

def test_parse_path_smoke(fs):

    pp = fs._parse_path("/people.mike")
    assert len(pp)==1
    assert pp[0]['tagType'] == "people"
    assert pp[0]['tagVal'] == "mike"
    
def test_parse_path_real(fs):

    pp = fs._parse_path("/people.mike/some/year.2018/tag1/tag2")
    assert len(pp)==5
    assert pp[0]['tagType'] == "people"
    assert pp[0]['tagVal'] == "mike"
    assert pp[1]['tagType'] == "tag"
    assert pp[1]['tagVal'] == "some"
    assert pp[2]['tagType'] == "year"
    assert pp[2]['tagVal'] == "2018"
    assert pp[3]['tagType'] == "tag"
    assert pp[3]['tagVal'] == "tag1"
    assert pp[4]['tagType'] == "tag"
    assert pp[4]['tagVal'] == "tag2"

def test_parse_path_dupl(fs):

    pp = fs._parse_path("/some/people.mike/some")
    assert len(pp)==2
    assert pp[1]['tagType'] == "people"
    assert pp[1]['tagVal'] == "mike"
    assert pp[0]['tagType'] == "tag"
    assert pp[0]['tagVal'] == "some"
    
def test_parse_path_slashes(fs):

    pp = fs._parse_path("//some///people.mike//some//")
    assert len(pp)==2
    assert pp[1]['tagType'] == "people"
    assert pp[1]['tagVal'] == "mike"
    assert pp[0]['tagType'] == "tag"
    assert pp[0]['tagVal'] == "some"

def test_parse_path_dots(fs):

    pp = fs._parse_path("/some/../../people.mike/../some")
    assert len(pp)==2
    assert pp[1]['tagType'] == "people"
    assert pp[1]['tagVal'] == "mike"
    assert pp[0]['tagType'] == "tag"
    assert pp[0]['tagVal'] == "some"

def test_parse_path_specials(fs):

    pp = fs._parse_path("/people.month/year.jpeg")
    assert len(pp)==2
    assert pp[0]['tagType'] == "people"
    assert pp[0]['tagVal'] == "month"
    assert pp[1]['tagType'] == "year"
    assert pp[1]['tagVal'] == "jpeg"

def test_parse_path_bad_types(fs):

    with pytest.raises(Exception) as ex:
        fs._parse_path("/peopl.mike/pic")
    assert ex.value.errno==errno.ENOTDIR

    with pytest.raises(Exception) as ex:
        fs._parse_path("/people.mike/pic.jpg")
    assert ex.value.errno==errno.ENOTDIR
    
def test_parse_path_dot_inname(fs):

    pp = fs._parse_path("/people.mike/year.2018.10")
    assert len(pp)==2
    assert pp[0]['tagType'] == "people"
    assert pp[0]['tagVal'] == "mike"
    assert pp[1]['tagType'] == "year"
    assert pp[1]['tagVal'] == "2018.10"
    
# ================================================ ADD_TAG
def test_add_tag_smoke(fs):

    assert fs._add_tag({'tagType': 'people','tagVal': 'mike' }) == True
    
def test_add_tag_dupl(fs):

    assert fs._add_tag({'tagType': 'people','tagVal': 'mike' }) == True
    assert fs._add_tag({'tagType': 'people','tagVal': 'mike' }) == False

def test_add_tag_badtype(fs):

    assert fs._add_tag({'tagType': 'bad','tagVal': 'mike' }) == False
    
def test_add_tag_real(fs):

    assert fs._add_tag({'tagType': 'people','tagVal': 'mike' }) == True
    assert fs._add_tag({'tagType': 'tag','tagVal': 'some' }) == True
    assert fs._add_tag({'tagType': 'tag','tagVal': 'another' }) == True

# ===================================================== MKDIR
def test_mkdir_smoke(fs):

    assert fs._check_tag({'tagType': 'people','tagVal': 'mike'}) == False
    fs.mkdir("/people.mike",1)
    assert fs._check_tag({'tagType': 'people','tagVal': 'mike'}) == True

def test_mkdir_existing(fs):

    fs.mkdir("/people.mike",1)
    with pytest.raises(Exception) as ex:
        fs.mkdir("/people.mike",1)
    assert ex.value.errno==errno.EEXIST
        
# ====================================================== ACCESS

def test_access_smoke(fs):

    fs.mkdir("/people.mike",1)
    assert fs.access("/people.mike",1) == True
    
def test_access_no_such_dir(fs):

    with pytest.raises(Exception) as ex:
        fs.access("/people.mike",1)
    assert ex.value.errno==errno.EACCES

def test_access_no_such_file(fs):

    fs.mkdir("/people.mike",1)
    with pytest.raises(Exception) as ex:
        fs.access("/people.mike/file.jpg",1)
    assert ex.value.errno==errno.EACCES
