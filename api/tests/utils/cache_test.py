from unittest.mock import MagicMock

from pcapi.routes.serialization import BaseModel
from pcapi.utils.cache import _CacheProxy
from pcapi.utils.cache import _compute_arguments_hash
from pcapi.utils.cache import _view_retriever
from pcapi.utils.cache import cached_view
from pcapi.utils.cache import get_from_cache


class DummySerializer(BaseModel):
    one: int | None
    two: str | None


class ViewRetrieverTest:
    def test_view_retriever_baseModel(self):
        view = MagicMock(return_value=DummySerializer(one=1, two="2"))
        result = _view_retriever(view, ["arg1", 2], {"key1": 1, "key2": "value2"})
        assert isinstance(result, str)
        assert result == '{"one": 1, "two": "2"}'
        view.assert_called_once_with("arg1", 2, key1=1, key2="value2")

    def test_view_retriever_str(self):
        view = MagicMock(return_value='{"one": 1, "two": "2"}')
        result = _view_retriever(view, ["arg1", 2], {"key1": 1, "key2": "value2"})
        assert isinstance(result, str)
        assert result == '{"one": 1, "two": "2"}'
        view.assert_called_once_with("arg1", 2, key1=1, key2="value2")


class ComputeArgumentsHashTest:
    def test_compute_arguments_hash_empty(self):
        result = _compute_arguments_hash([], {})
        assert result == "default"

    def test_compute_arguments_hash_args_only(self):
        result = _compute_arguments_hash([1, "arg1", DummySerializer(one=1, two="2")], {})
        assert result == "e1b09c882edc1ffc12f0636f9a9561bdee107f13e27494050825a2e699a25141"

    def test_compute_arguments_hash_kwargs_only(self):
        result = _compute_arguments_hash([], {"int": 1, "str": "arg1", "BaseModel": DummySerializer(one=1, two="2")})
        assert result == "ce718b5291b89b59ff21ea01e4917f76df4e71461097f64863f9888129864e91"

    def test_compute_arguments_hash_args_and_kwargs(self):
        result = _compute_arguments_hash(
            [1, "arg1", DummySerializer(one=1, two="2")],
            {"int": 12, "str": "arg12", "BaseModel": DummySerializer(one=12, two="22")},
        )
        assert result == "143fd0d3d3f5d859e8b00fbe00de6700c86ea7a8eee1d0cf5da9dd19b070a95c"


class CachedViewTest:
    def test_cached_view_basic_usage(self):
        x = 1

        @cached_view()
        def dummy_view_test1():
            if x == 1:
                return DummySerializer(one=1, two="2")
            return None

        first_call = dummy_view_test1()
        x += 1
        second_call = dummy_view_test1()
        expected_json = '{"one": 1, "two": "2"}'
        assert first_call.json() == expected_json
        assert isinstance(first_call, _CacheProxy)
        assert second_call.json() == expected_json
        assert isinstance(second_call, _CacheProxy)

    def test_cached_view_default_only_activated(self):
        x = 1

        @cached_view(cache_only_if_no_arguments=True)
        def dummy_view_test2(argument=1):
            if argument == 1:
                return DummySerializer(one=x, two="2")
            return DummySerializer(one=x, two="argument")

        first_call = dummy_view_test2()
        x += 1
        second_call = dummy_view_test2(2)
        x += 1
        third_call = dummy_view_test2(2)
        x += 1
        fourth_call = dummy_view_test2()
        x += 1
        fifth_call = dummy_view_test2(3)
        assert first_call.json() == '{"one": 1, "two": "2"}'
        assert second_call.json() == '{"one": 2, "two": "argument"}'
        assert third_call.json() == '{"one": 3, "two": "argument"}'
        assert fourth_call.json() == '{"one": 1, "two": "2"}'
        assert fifth_call.json() == '{"one": 5, "two": "argument"}'

    def test_cached_view_default_only_deactivated(self):
        x = 1

        @cached_view(cache_only_if_no_arguments=False)
        def dummy_view_test2(argument=1):
            if argument == 1:
                return DummySerializer(one=x, two="2")
            return DummySerializer(one=x, two="argument")

        first_call = dummy_view_test2()
        x += 1
        second_call = dummy_view_test2(2)
        x += 1
        third_call = dummy_view_test2(2)
        x += 1
        fourth_call = dummy_view_test2()
        x += 1
        fifth_call = dummy_view_test2(3)
        assert first_call.json() == '{"one": 1, "two": "2"}'
        assert second_call.json() == '{"one": 2, "two": "argument"}'
        assert third_call.json() == '{"one": 2, "two": "argument"}'
        assert fourth_call.json() == '{"one": 1, "two": "2"}'
        assert fifth_call.json() == '{"one": 5, "two": "argument"}'

    def test_cached_view_ignore_args_activated(self):
        x = 1

        @cached_view(ignore_args=True)
        def dummy_view_test3(argument=1):
            if argument == 1:
                return DummySerializer(one=x, two="2")
            return DummySerializer(one=x, two="argument")

        first_call = dummy_view_test3()
        x += 1
        second_call = dummy_view_test3(2)
        x += 1
        third_call = dummy_view_test3(2)
        x += 1
        fourth_call = dummy_view_test3()
        x += 1
        fifth_call = dummy_view_test3(3)
        assert first_call.json() == '{"one": 1, "two": "2"}'
        assert second_call.json() == '{"one": 1, "two": "2"}'
        assert third_call.json() == '{"one": 1, "two": "2"}'
        assert fourth_call.json() == '{"one": 1, "two": "2"}'
        assert fifth_call.json() == '{"one": 1, "two": "2"}'


class GetFromCacheTest:
    def test_force_update_off(self):
        result1 = get_from_cache(
            key_template="test_force_update_off",
            retriever=MagicMock(return_value="pouet"),
        )
        retriever = MagicMock(return_value="pouet2")
        result2 = get_from_cache(
            key_template="test_force_update_off",
            retriever=retriever,
            force_update=False,
        )
        assert result1 == result2
        assert result2 == "pouet"
        retriever.assert_not_called()

    def test_force_update_on(self):
        result1 = get_from_cache(
            key_template="test_force_update_off",
            retriever=MagicMock(return_value="pouet"),
        )
        retriever = MagicMock(return_value="pouet2")
        result2 = get_from_cache(
            key_template="test_force_update_off",
            retriever=retriever,
            force_update=True,
        )
        assert result1 != result2
        assert result2 == "pouet2"
        retriever.assert_called_once()
