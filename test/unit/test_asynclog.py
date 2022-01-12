class FakeReq(dict):
    def __init__(self, *args, **kwargs):
        trazability = dict(logging={'app_name': 'foo'})
        self.update(dict(trazability=trazability))
        super().__init__(*args, **kwargs)
    res = 1


def test_asynclog_in_middleware(writer):
    from laozi.asynclog import AiohttpLogger

    async def test(request):
        return request.res

    async def do_test():
        log = AiohttpLogger(test(request=FakeReq(a=1)))
        log.logger.add(writer, format="{message}")
        await log.info

    import asyncio
    asyncio.run(do_test())

    assert writer.read() == "starting_test\nfinished_test\n"


def test_asynclog_in_middleware_views(writer):
    from laozi.asynclog import AiohttpLogger

    class TestView:
        def __init__(self):
            self.request = FakeReq(a=1)

        async def get(self):
            return self.request.res

    async def do_test():
        log = AiohttpLogger(TestView().get())
        log.logger.add(writer, format="{message}")
        await log.info

    import asyncio
    asyncio.run(do_test())

    assert writer.read() == "starting_get\nfinished_get\n"


def test_asynclog_in_handler(writer):
    from laozi.asynclog import AiohttpLogger

    async def test_coro(a, b):
        return a + b

    async def handler(request):  # noqa
        log = AiohttpLogger(test_coro(1, 2))
        log.logger.add(writer, format="{message}")
        await log.info

    import asyncio
    asyncio.run(handler(FakeReq(a=1)))

    assert writer.read() == "starting_test_coro\nfinished_test_coro\n"


def test_with_loguru(writer):
    from laozi import Laozi
    from loguru import logger
    from laozi.asynclog import AiohttpLogger
    import asyncio

    def formatter(record):
        record['extra']['formatted'] = Laozi.parse(record['extra'])
        return ('{message}; {extra[formatted]}\n{exception}')

    async def test_coro(a, b):
        return a + b

    async def handler(request):  # noqa
        print("INSIDE")
        print(request)
        await AiohttpLogger(test_coro(1, 2)).info

    print(FakeReq(a=2))

    logger.remove()
    logger.add(writer, format=formatter, level="INFO")
    asyncio.run(handler(FakeReq(a=2)))

    exp = ('starting_test_coro; extra.app_name="foo"; '
           'extra.params.a=1; extra.params.b=2\nfinished_test_coro; '
           'extra.app_name="foo"; extra.result=3\n')

    assert writer.read() == exp


def test_lmc_with_loguru(writer):
    from laozi import Laozi
    from loguru import logger
    from laozi.asynclog import LoggableMethodsClass
    import asyncio

    class MyModel(LoggableMethodsClass):
        async def test_coro(self, a, b):
            return a + b

    def formatter(record):
        record['extra']['formatted'] = Laozi.parse(record['extra'])
        return ('{message}; {extra[formatted]}\n{exception}')

    async def handler(request):  # noqa
        await MyModel().test_coro(1, 2).info
        return request.res

    logger.remove()
    logger.add(writer, format=formatter, level="INFO")
    asyncio.run(handler(FakeReq(a=2)))

    exp = ('starting_test_coro; extra.app_name="foo"; '
           'extra.params.a=1; extra.params.b=2\nfinished_test_coro; '
           'extra.app_name="foo"; extra.result=3\n')

    assert writer.read() == exp
