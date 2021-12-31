# -*- coding: utf-8 -*-
# pylint: disable=no-self-use

import pytest
from collectd import CollecdMock
from collectd.values import Values

from sumologic_collectd_metrics.metrics_converter import (
    convert_to_metrics,
    gen_tag,
    parse_statsd_signalfx_metric_name,
    tags_to_str,
)


def test_gen_tag():
    assert gen_tag("tag_key", "tag_value") == "tag_key=tag_value"


def test_gen_tag_empty_value():
    assert gen_tag("tag_key", "") == ""


def test_gen_tag_empty_key_exception():
    with pytest.raises(Exception) as e:
        gen_tag("", "tag_value")

    assert "Key for value tag_value cannot be empty" in str(e)


def test_gen_tag_key_word_exception():
    with pytest.raises(Exception) as e:
        gen_tag("_sourceId", "tag_value")

    assert "Key _sourceId (case-insensitive) must not contain reserved keywords" in str(
        e
    )


def test_gen_key_not_string_exception():
    value = gen_tag(("tag_key",), "tag_value")
    expected = "[('tag_key',)=tag_value"

    assert expected, value


def test_gen_value_not_string_exception():
    value = gen_tag(("tag_key",), 1)
    expected = "tag_key=1"

    assert expected, value


def test_gen_value_reserved():
    assert (
        gen_tag("tag_key space=", "tag_value=t st") == "tag_key_space:=tag_value:t_st"
    )


def test_tags_to_str():
    tags = ["tag_key1=tag_val1", "tag_key2=tag_val2", "tag_key3=tag_val3"]
    tag_str = tags_to_str(tags)

    assert tag_str == "tag_key1=tag_val1 tag_key2=tag_val2 tag_key3=tag_val3"


def test_tags_to_str_with_empty_tag():
    tags = ["tag_key1=tag_val1", "", "tag_key3=tag_val3"]
    tag_str = tags_to_str(tags)

    assert tag_str == "tag_key1=tag_val1 tag_key3=tag_val3"


def test_tags_to_str_with_empty_tags():
    tags = []
    tag_str = tags_to_str(tags)

    assert tag_str == ""


def test_convert_to_metrics_single():
    data = Values()
    dataset = CollecdMock().get_dataset("test_type")
    metrics = convert_to_metrics(data, dataset, None)

    assert metrics == data.metrics_str(None)


def test_convert_to_metrics_multiple():
    data = Values(
        type="test_type_2",
        values=[1.23, 4.56],
        ds_names=["test_ds_name1", "test_ds_name2"],
        ds_types=["test_ds_type1", "test_ds_type2"],
    )
    dataset = CollecdMock().get_dataset("test_type_2")
    metrics = convert_to_metrics(data, dataset, None)

    assert metrics == data.metrics_str(None)


def test_convert_to_metrics_no_meta():
    data = Values(
        type="test_type_2",
        meta={},
        values=[1.23, 4.56],
        ds_names=["test_ds_name1", "test_ds_name2"],
        ds_types=["test_ds_type1", "test_ds_type2"],
    )
    dataset = CollecdMock().get_dataset("test_type_2")
    metrics = convert_to_metrics(data, dataset, None)

    assert metrics == data.metrics_str(None)


def test_convert_to_metrics_with_metric_dimension():
    data = Values()
    dataset = CollecdMock().get_dataset("test_type")
    metrics = convert_to_metrics(data, dataset, "_")

    assert metrics == data.metrics_str("_")


class TestParseStatsDSignalFxMetricName:
    @pytest.mark.parametrize(
        "metric_name",
        ("some_name", "name_with_[", "name_with_]", "name_with.[]empty_tag_section"),
    )
    def test_no_tags(self, metric_name):
        assert parse_statsd_signalfx_metric_name(metric_name) == (metric_name, {})

    @pytest.mark.parametrize(
        "metric_name,log_message",
        [
            (
                "two[key=value]sections[key=value]",
                "Found more than one metadata segment in metric name "
                "`two[key=value]sections[key=value]`. Ignoring all segments.",
            ),
            (
                "no[key]value",
                "Invalid key=value pair `key` in metric name `no[key]value`, ignoring it",
            ),
            (
                "no[=value]key",
                "Empty keys aren't supported, ignoring key=value pair `=value` in metric name "
                "`no[=value]key`",
            ),
        ],
    )
    def test_invalid_format(self, metric_name, log_message, caplog):
        assert parse_statsd_signalfx_metric_name(metric_name) == (metric_name, {})
        assert len(caplog.messages) == 1
        assert caplog.messages[0] == log_message

    @pytest.mark.parametrize(
        "metric_name,cleaned_name,metadata,log_message",
        [
            (
                "metric.[key=value]test",
                "metric.test",
                dict(key="value"),
                None,
            ),
            (
                "metric.[key1=value1,key2=value2]test",
                "metric.test",
                dict(key1="value1", key2="value2"),
                None,
            ),
            (
                "ignore[key1=value1, key2].malformed",
                "ignore.malformed",
                dict(key1="value1"),
                "Invalid key=value pair `key2` in metric name `ignore[key1=value1, key2].malformed`"
                ", ignoring it",
            ),
            (
                "ignore[key=value1, key=value2].duplicates",
                "ignore.duplicates",
                dict(key="value1"),
                "Key `key` is defined multiple times in metric name "
                "`ignore[key=value1, key=value2].duplicates`, ignoring subsequent values",
            ),
            (
                "spaces[ key = value ]",
                "spaces",
                dict(key="value"),
                None,
            ),
        ],
    )
    def test_valid_tags(self, metric_name, cleaned_name, metadata, log_message, caplog):
        assert parse_statsd_signalfx_metric_name(metric_name) == (
            cleaned_name,
            metadata,
        )
        if log_message is not None:
            assert len(caplog.messages) == 1
            assert caplog.messages[0] == log_message
