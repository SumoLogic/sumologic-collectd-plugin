import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/sumologic_collectd_metrics')
import pytest
from metrics_converter import gen_tag, tags_to_str, convert_to_metrics
from collectd.values import Values
from collectd import Helper


def test_gen_tag():
    assert gen_tag('tag_key', 'tag_value') == 'tag_key=tag_value'


def test_gen_tag_empty_value():
    assert gen_tag('tag_key', '') == ''


def test_gen_tag_empty_key_exception():
    with pytest.raises(Exception) as e:
        gen_tag('', 'tag_value')

    assert 'Key for value tag_value cannot be empty' in str(e)


def test_gen_tag_key_word_exception():
    with pytest.raises(Exception) as e:
        gen_tag('_sourceId', 'tag_value')

    assert 'Key _sourceId (case-insensitive) must not contain reserved keywords' in str(e)


def test_gen_key_not_string_exception():
    with pytest.raises(Exception) as e:
        gen_tag(('tag_key', ), 'tag_value')

    assert "Key ('tag_key',) for Value tag_value must be string type." in str(e)


def test_gen_value_not_string_exception():
    with pytest.raises(Exception) as e:
        gen_tag('tag_key', 1)

    assert "Value 1 for Key tag_key must be string type." in str(e)


def test_tags_to_str():
    tags = ['tag_key1=tag_val1', 'tag_key2=tag_val2', 'tag_key3=tag_val3']
    tag_str = tags_to_str(tags)

    assert tag_str == 'tag_key1=tag_val1 tag_key2=tag_val2 tag_key3=tag_val3'


def test_tags_to_str_with_empty_tag():
    tags = ['tag_key1=tag_val1', '', 'tag_key3=tag_val3']
    tag_str = tags_to_str(tags)

    assert tag_str == 'tag_key1=tag_val1 tag_key3=tag_val3'


def test_tags_to_str_with_empty_tags():
    tags = []
    tag_str = tags_to_str(tags)

    assert tag_str == ''


def test_convert_to_metrics_single():
    d = Values()
    helper = Helper()
    metrics = convert_to_metrics(d, helper.types)

    assert metrics == d.metrics_str()


def test_convert_to_metrics_multiple():
    d = Values(type='test_type_2', values=[1.23, 4.56], ds_names=['test_ds_name1', 'test_ds_name2'],
               ds_types=['test_ds_type1', 'test_ds_type2'])
    helper = Helper()
    metrics = convert_to_metrics(d, helper.types)

    assert metrics == d.metrics_str()


def test_convert_to_metrics_no_meta():
    d = Values(type='test_type_2', meta={}, values=[1.23, 4.56],
               ds_names=['test_ds_name1', 'test_ds_name2'],
               ds_types=['test_ds_type1', 'test_ds_type2'])
    helper = Helper()
    metrics = convert_to_metrics(d, helper.types)

    assert metrics == d.metrics_str()


def test_convert_to_metrics_type_format_exception():
    with pytest.raises(Exception) as e:
        d = Values(type='test_type_2', values=[1.23], ds_names=['test_ds_name1', 'test_ds_name2'],
                   ds_types=['test_ds_type1', 'test_ds_type2'])
        helper = Helper()
        convert_to_metrics(d, helper.types)

    assert 'Number values [1.23] differ from types defined for test_type_2' in str(e)


def test_convert_to_metrics_type_nonexist_exception():
    with pytest.raises(Exception) as e:
        d = Values(type='test_type_3', values=[1.23], ds_names=['test_ds_name1', 'test_ds_name2'],
                   ds_types=['test_ds_type1', 'test_ds_type2'])
        helper = Helper()
        convert_to_metrics(d, helper.types)

    assert 'Do not know how to handle type test_type_3. ' \
           'Do you have all your types.db files configured?' in str(e)
