def fake(object_type):
    class FakeObject(object_type):
        def __eq__(self, other_object):
            return isinstance(other_object, object_type)

    return FakeObject()
