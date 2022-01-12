import logging
import asyncio
import typing
import sys
from aiohttp.web import Response

import loguru

LEVELS: set = {a.lower() for a in logging._levelToName.values()}
DLG = ("self", "request", 'handler', 'old_handler', 'cls')

logging.basicConfig(level=logging.INFO)


class AiohttpLogger:
    """Magic coroutine logging.

    Allows wrapping coroutines to automatically log its up/down.

    >>> await Logger(coro(1, 2)).info

    """
    def __init__(self, coro, conds=None):
        """Set coroutine, state by default is debug"""
        self.coro: typing.Coroutine = coro
        self.state: str = 'debug'
        self.request_conds = conds
        self.logger: loguru.Logger = loguru.logger

    def __getattr__(self, attr: str):
        """Set requested attribute as state if attr is in loglevels.

        Whenever we request a .info .debug etc, do not return original attr
        """
        if attr in LEVELS:
            self.state = attr
            return self
        if attr == 'request':
            self.state = 'request'
            return self
        raise AttributeError

    def __call__(self, *args, **kwargs):
        self.params = (args, kwargs)
        return self

    def __await__(self):
        """Make ourselves awaitable."""
        # Allow coroutine functions, delegating in calling ourselves via
        # __call__

        # Allow for a special .request for middlewares
        # use as await Logger(handler(request)).request
        is_request = False
        state = self.state
        if state == 'request':
            state = 'INFO'
            is_request = True
        state = state.upper()

        if asyncio.iscoroutinefunction(self.coro):
            self.coro = self.coro(*self.params[0], **self.params[1])

        frame = self.coro.cr_frame
        coro_locals = frame.f_locals
        # Allow logging both aiohttp handlers directly (i.e inside a custom
        # middleware) or coroutines called inside, both for class-based views
        # and normal views.
        request = coro_locals.get(
            'request', getattr(coro_locals.get('self'), 'request', None))
        if not request:
            _locals = sys._getframe(1).f_locals
            request = _locals.get(
                'request', getattr(_locals.get('self'), 'request', None))

        dont_log = False
        if self.request_conds:
            dont_log = self.request_conds(request)

        if not request or dont_log:
            result = yield from self.coro.__await__()
            return result

        name: str = frame.f_code.co_name

        start = f'starting_{name}'
        end = f'finished_{name}'

        #: Assign to your request a trazability dict with a logging key
        #: on your custom middleware to log trazability info on each log in
        #: this request
        trz: dict = request.get('trazability', {}).get('logging', {})
        coro_locals = {a: b for a, b in coro_locals.items() if a not in DLG}
        if is_request:
            trz |= {'url': str(request.url), 'method': request.method}
            start = 'request_received'
            end = 'response_sent'
        self.logger.log(state, start, extra=trz | {'params': coro_locals})
        raise_exc = None
        try:
            res = yield from self.coro.__await__()
        except Exception as err:
            state = 'ERROR'
            raise_exc = err
            res = {
                'exception': str(err),
                'exception_class': err.__class__.__name__
            }
            end = 'http_error' if is_request else 'exception'

        if isinstance(res, Response):
            trz['code'] = res.status

        self.logger.log(state, end, extra=trz | dict(result=res))

        if raise_exc:
            raise raise_exc
        return res


class LoggableMethodsClass:
    """Auto-log coroutine methods start and end

        >>> class Test(LoggableMethodsClass):
        ...     async def test_cor(self, a, b):
        ...         return a + b

        >>> await Test().test_cor(1, 2).info
    """
    def __getattribute__(self, name):
        parent = super().__getattribute__(name)
        if asyncio.iscoroutinefunction(parent):
            return AiohttpLogger(parent)
        return super().__getattribute__(name)
