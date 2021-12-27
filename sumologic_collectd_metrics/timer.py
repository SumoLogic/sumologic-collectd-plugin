# -*- coding: utf-8 -*-

import threading


class Timer:
    """
    Event scheduler with start, cancel, and reset
    """

    def __init__(self, interval, task):
        self.interval = interval
        self.task = task
        self.timer = None
        self.start_timer_lock = threading.Lock()
        self.run_count = 0
        self.run_count_reset = 60 / interval
        if hasattr(self, "collectd"):
            self.collectd.info(
                "Timer %s will report once a minute (every %s runs)."
                % (self.__class__.__name__, self.run_count_reset)
            )

    def __del__(self):
        self.cancel_timer()

    def start_timer(self):
        """
        Start a thread to periodically run task func
        """

        with self.start_timer_lock:
            if hasattr(self, "collectd"):
                self.collectd.debug("Timer has been run: %s." % self.__class__.__name__)
            if self.run_count >= self.run_count_reset:
                if hasattr(self, "collectd"):
                    self.collectd.info(
                        "Timer %s has run %s times."
                        % (self.__class__.__name__, self.run_count)
                    )
                self.run_count = 0
            self.run_count += 1

            self.timer = threading.Timer(self.interval, self.start_timer)
            self.timer.daemon = True
            self.timer.start()

        self.task()

    def cancel_timer(self):
        if hasattr(self, "collectd"):
            self.collectd.debug(
                "Timer has been canceled: %s." % self.__class__.__name__
            )
        if self.timer is not None:
            self.timer.cancel()

    def reset_timer(self):
        if hasattr(self, "collectd"):
            self.collectd.debug("Timer has been reset: %s" % self.__class__.__name__)
        self.cancel_timer()
        self.start_timer()
