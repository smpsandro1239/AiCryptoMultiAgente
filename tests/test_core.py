import unittest
import asyncio
from multiagent_trading.core.orchestrator import EventBus

class TestEventBus(unittest.TestCase):
    def test_subscribe_publish(self):
        bus = EventBus()
        received = []
        async def callback(data):
            received.append(data)

        bus.subscribe("test", callback)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bus.publish("test", "hello"))

        self.assertEqual(received, ["hello"])

if __name__ == "__main__":
    unittest.main()
