import threading


class Timer:

    def __init__(self, interval, task):
        self.interval = interval
        self.task = task
        self.timer = None

    def __del__(self):
        self.cancel_timer()

    def start_timer(self):
        """
        Start a thread to periodically run task func
        """

        self.timer = threading.Timer(self.interval, self.start_timer)
        self.timer.daemon = True
        self.timer.start()

        self.task()

    def cancel_timer(self):
        if self.timer is not None:
            self.timer.cancel()

    def reset_timer(self):
        self.cancel_timer()
        self.start_timer()