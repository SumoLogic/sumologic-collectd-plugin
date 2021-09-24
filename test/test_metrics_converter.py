# -*- coding: utf-8 -*-

import pytest

from collectd import CollecdMock
from collectd.values import Values

from sumologic_collectd_metrics.metrics_converter import (convert_to_metrics,
                                                          gen_tag, tags_to_str)


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
    value = gen_tag(('tag_key', ), 'tag_value')
    expected = '[(\'tag_key\',)=tag_value'

    assert expected, value


def test_gen_value_not_string_exception():
    value = gen_tag(('tag_key', ), 1)
    expected = 'tag_key=1'

    assert expected, value


def test_gen_value_reserved():
    assert gen_tag('tag_key space=', 'tag_value=t st') == 'tag_key_space:=tag_value:t_st'


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
    data = Values()
    dataset = CollecdMock().get_dataset('test_type')
    metrics = convert_to_metrics(data, dataset, None)

    assert metrics == data.metrics_str(None)


def test_convert_to_metrics_multiple():
    data = Values(type='test_type_2', values=[1.23, 4.56],
                  ds_names=['test_ds_name1', 'test_ds_name2'],
                  ds_types=['test_ds_type1', 'test_ds_type2'])
    dataset = CollecdMock().get_dataset('test_type_2')
    metrics = convert_to_metrics(data, dataset, None)

    assert metrics == data.metrics_str(None)


def test_convert_to_metrics_no_meta():
    data = Values(type='test_type_2', meta={}, values=[1.23, 4.56],
                  ds_names=['test_ds_name1', 'test_ds_name2'],
                  ds_types=['test_ds_type1', 'test_ds_type2'])
    dataset = CollecdMock().get_dataset('test_type_2')
    metrics = convert_to_metrics(data, dataset, None)

    assert metrics == data.metrics_str(None)


def test_convert_to_metrics_with_metric_dimension():
    data = Values()
    dataset = CollecdMock().get_dataset('test_type')
    metrics = convert_to_metrics(data, dataset, '_')

    assert metrics == data.metrics_str('_')
