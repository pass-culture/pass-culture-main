from pcapi.utils import queue


class AddToQueueTest:
    def test_should_add_item_to_queue(self, app):
        first_item = {"one": 1, "two": "2"}
        second_item = {"one": 3, "two": "4"}
        third_item = {"one": 5, "two": "6"}
        queue.add_to_queue("test:numbers", first_item)
        queue.add_to_queue("test:numbers", second_item)
        queue.add_to_queue("test:numbers", third_item, at_head=True)

        numbers = app.redis_client.lrange("test:numbers", 0, -1)
        assert len(numbers) == 3
        assert numbers == ['{"one": 5, "two": "6"}', '{"one": 1, "two": "2"}', '{"one": 3, "two": "4"}']


class PopFromQueueTest:
    def test_should_pop_items_from_queue(self):
        queue.add_to_queue("test:numbers", {"one": 1, "two": "2"})
        queue.add_to_queue("test:numbers", {"one": 3, "two": "4"})

        first_item = queue.pop_from_queue("test:numbers")
        assert first_item == {"one": 1, "two": "2"}

        second_item = queue.pop_from_queue("test:numbers")
        assert second_item == {"one": 3, "two": "4"}

        third_item = queue.pop_from_queue("test:numbers")
        assert not third_item
