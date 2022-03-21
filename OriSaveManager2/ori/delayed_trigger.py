import threading


class DelayedTrigger:
    def __init__(self, func, *, delay):
        self._delay = delay
        self._func = func
        self._timer = None

    def __call__(self, *args, **kwargs):
        self.cancel()
        self._timer = threading.Timer(self._delay, self._func, args=args, kwargs=kwargs)
        self._timer.start()

    def cancel(self):
        if self._timer is not None:
            self._timer.cancel()
