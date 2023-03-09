import pytest
from hypothesis import given
from hypothesis.strategies import text, just
from file_search_4a import get_displayable_name

@given(zipname=text(), filename=text())
def test_get_displayable_name(zipname, filename):
    file = f"{zipname}!{filename}"
    result = get_displayable_name(file)
    expected = f"{zipname} ({filename})"
    assert result == expected

def test_get_displayable_name_with_no_zip():
    file = "filename.txt"
    result = get_displayable_name(file)
    assert result == file