from shapely.geometry import Polygon


def fake(object_type):
    class FakeObject(object_type):
        def __eq__(self, other_object):
            return isinstance(other_object, object_type)

    return FakeObject()


POLYGON_TEST = Polygon([(2.195693, 49.994169), (2.195693, 47.894173), (2.595697, 47.894173), (2.595697, 49.994169)])
