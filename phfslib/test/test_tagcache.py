import pytest
import errno

import tagcache as tc

@pytest.fixture
def stc():
    """ стандартный setup для всех тестов """
    return tc.TagCache([ "people","year","month","day","geo","tag" ])

# ======================================== INIT
def test_init_smoke(stc):

    assert "people" in stc.tagTypes
    assert "year" in stc.tagTypes
    assert "month" in stc.tagTypes
    assert "day" in stc.tagTypes
    assert "geo" in stc.tagTypes
    assert "tag" in stc.tagTypes

# ========================================= parseDirPath
def test_parseDirPath_smoke(stc):

    res = stc._parseDirPath("/people.mike")
    assert len(res)==1
    assert res[0]['tagType'] == "people"
    assert res[0]['tagVal'] == "mike"
    
def test_parseDirPath_real(stc):

    pp = stc._parseDirPath("/people.mike/tag.some/year.2018/tag.tag1")
    assert len(pp)==4
    assert pp[0]['tagType'] == "people"
    assert pp[0]['tagVal'] == "mike"
    assert pp[1]['tagType'] == "tag"
    assert pp[1]['tagVal'] == "some"
    assert pp[2]['tagType'] == "year"
    assert pp[2]['tagVal'] == "2018"
    assert pp[3]['tagType'] == "tag"
    assert pp[3]['tagVal'] == "tag1"

def test_parseDirPath_dupl(stc):

    pp = stc._parseDirPath("/tag.some/people.mike/tag.some")
    assert len(pp)==2
    assert pp[0]['tagType'] == "tag"
    assert pp[0]['tagVal'] == "some"
    assert pp[1]['tagType'] == "people"
    assert pp[1]['tagVal'] == "mike"
    
def test_parseDirPath_slashes(stc):

    pp = stc._parseDirPath("//tag.some///people.mike//tag.some//")
    assert len(pp)==2
    assert pp[0]['tagType'] == "tag"
    assert pp[0]['tagVal'] == "some"
    assert pp[1]['tagType'] == "people"
    assert pp[1]['tagVal'] == "mike"

def test_parseDeiPath_dots(stc):

    pp = stc._parseDirPath("/tag.some/../../people.mike/../tag.some")
    assert len(pp)==2
    assert pp[0]['tagType'] == "tag"
    assert pp[0]['tagVal'] == "some"
    assert pp[1]['tagType'] == "people"
    assert pp[1]['tagVal'] == "mike"

def test_parseDirPath_specials(stc):

    pp = stc._parseDirPath("/people.month/year.jpeg")
    assert len(pp)==2
    assert pp[0]['tagType'] == "people"
    assert pp[0]['tagVal'] == "month"
    assert pp[1]['tagType'] == "year"
    assert pp[1]['tagVal'] == "jpeg"
    
def test_parseDirPath_bad_types(stc):

    with pytest.raises(Exception) as ex:
        stc._parseDirPath("/peopl.mike/tag.some")
    assert ex.typename=="BadTagType"

    with pytest.raises(Exception) as ex:
        stc._parseDirPath("/people.mike/pic")
    assert ex.typename=="NoTagType"
    
def test_parseDirPath_dot_inname(stc):

    pp = stc._parseDirPath("/people.mike/year.2018.10")
    assert len(pp)==2
    assert pp[0]['tagType'] == "people"
    assert pp[0]['tagVal'] == "mike"
    assert pp[1]['tagType'] == "year"
    assert pp[1]['tagVal'] == "2018.10"

# ========================================== addDirPath

def test_addDirPath_smoke(stc):

    stc.addDirPath("/people.mike/year.2018")
    assert 'mike' in stc.tags['people']
    assert '2018' in stc.tags['year']

def test_addDirPath_bad_types(stc):

    with pytest.raises(Exception) as ex:
        stc.addDirPath("/peopl.mike/tag.some")
    assert ex.typename=="BadTagType"

    with pytest.raises(Exception) as ex:
        stc.addDirPath("/people.mike/pic")
    assert ex.typename=="NoTagType"

# =========================================== checkDirPath

def test_checkDirPath_smoke(stc):

    assert stc.checkDirPath("/people.mike")==False
    stc.addDirPath("/people.mike")
    assert stc.checkDirPath("/people.mike")==True

def test_checkDirPath_bad_types(stc):

    with pytest.raises(Exception) as ex:
        stc.checkDirPath("/peopl.mike/tag.some")
    assert ex.typename=="BadTagType"

    with pytest.raises(Exception) as ex:
        stc.checkDirPath("/people.mike/pic")
    assert ex.typename=="NoTagType"
    
def test_checkDirPath_subpath(stc):

    stc.addDirPath("/people.mike/year.2018")
    assert stc.checkDirPath("/people.mike")==True
    assert stc.checkDirPath("/year.2018")==True

def test_checkDirPath_order(stc):

    stc.addDirPath("/people.mike/year.2018")
    assert stc.checkDirPath("/people.mike/year.2018")==True
    assert stc.checkDirPath("/year.2018/people.mike")==True
