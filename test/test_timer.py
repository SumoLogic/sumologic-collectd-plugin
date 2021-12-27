# -*- coding: utf-8 -*-

from sumologic_collectd_metrics.timer import Timer


def test_cancel_timer_normal():
    timer = Timer(0.1, task)
    timer.start_timer()

    assert timer.timer is not None

    timer.cancel_timer()


def test_cancel_timer_not_start():
    timer = Timer(0.1, task)

    assert timer.timer is None

    timer.cancel_timer()


def test_reset_timer_normal():
    timer = Timer(0.1, task)
    timer.start_timer()

    assert timer.timer is not None

    timer.reset_timer()

    assert timer.timer is not None

    timer.cancel_timer()


def test_reset_timer_not_start():
    timer = Timer(0.1, task)

    assert timer.timer is None

    timer.reset_timer()

    assert timer.timer is not None

    timer.cancel_timer()


def task():
    print("Timer task ... ")
