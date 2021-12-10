import logging
import asyncio
import typing
import sys

import loguru

LEVELS: set = {a.lower() for a in logging._levelToName.values()}

logging.basicConfig(level=logging.INFO)


class AiohttpLogger:
    """Magic coroutine logging.

    Allows wrapping coroutines to automatically log its up/down.

    >>> await Logger(coro(1, 2)).info

    """
    def __init__(self, coro):
        """Set coroutine, state by default is debug"""
        self.coro: typing.Coroutine = coro
        self.state: str = 'debug'
        self.logger: loguru.Logger = loguru.logger

    def __getattr__(self, attr: str):
        """Set requested attribute as state if attr is in loglevels.

        Whenever we request a .info .debug etc, do not return original attr
        """
        if attr in LEVELS:
            self.state = attr
            return self
        raise AttributeError

    def __call__(self, *args, **kwargs):
        self.params = (args, kwargs)
        return self

    def __await__(self):
        """Make ourselves awaitable."""
        # Allow coroutine functions, delegating in calling ourselves via
        # __call__
        if asyncio.iscoroutinefunction(self.coro):
            self.coro = self.coro(*self.params[0], **self.params[1])

        coro_locals = self.coro.cr_frame.f_locals
        # Allow logging both aiohttp handlers directly (i.e inside a custom
        # middleware) or coroutines called inside, both for class-based views
        # and normal views.
        request = coro_locals.get(
            'request', getattr(coro_locals.get('self'), 'request', None))
        if not request:
            _locals = sys._getframe(1).f_locals
            request = _locals.get('request',
                                  getattr(_locals.get('self'), 'request', None))

        if not request:
            result = yield from self.coro.__await__()
            return result

        state: int = logging._nameToLevel.get(self.state.upper(), 10)
        name: str = self.coro.cr_frame.f_code.co_name
        trz: dict = request.trazability

        self.logger.log(state,
                        f'starting_{name}',
                        extra=trz | {'params': self.coro.cr_frame.f_locals})
        result = yield from self.coro.__await__()
        self.logger.log(state,
                        f'finished_{name}',
                        extra=trz | dict(result=result))
        return result


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
