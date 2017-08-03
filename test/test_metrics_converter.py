import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')
import pytest
from metrics_converter import MetricsConverter


def test_convert_to_mtrics():
    pass


def test_gen_tag_empty_key_exception():
    with pytest.raises(Exception) as e:
        MetricsConverter.gen_tag('', 'tag_value')

    assert 'Key for value tag_value cannot be empty' in str(e.value)


def test_gen_tag_key_word_exception():
    with pytest.raises(Exception) as e:
        MetricsConverter.gen_tag('_sourceId', 'tag_value')

    assert 'Key _sourceId (case-insensitive) must not contain reserved keywords' in str(e.value)


def test_gen_tag_empty_value():
    assert MetricsConverter.gen_tag('tag_key', '') == ''


def test_gen_key_not_string_exception():
    with pytest.raises(Exception) as e:
        MetricsConverter.gen_tag(('tag_key', ), 'tag_value')

    assert "Field ('tag_key',) must be string type. Type is <type 'tuple'>" in str(e.value)


def test_gen_value_not_string_exception():
    with pytest.raises(Exception) as e:
        MetricsConverter.gen_tag('tag_key', 1)

    assert "Field 1 must be string type. Type is <type 'int'>" in str(e.value)
