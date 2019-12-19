from datetime import datetime
from glob import glob
from inspect import isclass

import pytest

import models
from local_providers.providable_info import ProvidableInfo
from models import PcObject, Provider, Product
from models.db import Model
from repository.provider_queries import get_provider_by_local_class
from utils.object_storage import STORAGE_DIR


def saveCounts():
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isclass(model) \
                and issubclass(model, PcObject) \
                and modelName != "PcObject":
            saved_counts[modelName] = model.query.count()


def assertCreatedCounts(**counts):
    for modelName in counts:
        model = getattr(models, modelName)
        all_records_count = model.query.count()
        previous_records_count = saved_counts[modelName]
        last_created_count = all_records_count - previous_records_count
        assert last_created_count == counts[modelName], \
            'Model [%s], Actual [%s], Expected [%s]' % (modelName, last_created_count, counts[modelName])


def assertEmptyDb():
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isinstance(model, PcObject):
            if modelName == 'Mediation':
                assert model.query.count() == 2
            else:
                assert model.query.count() == 0


def assert_created_thumbs():
    assert len(glob(str(STORAGE_DIR / "thumbs" / "*"))) == 1


def provider_test(app, provider, venue_provider, **counts):
    if venue_provider is None:
        provider_object = provider()
    else:
        provider_object = provider(venue_provider)
    provider_object.provider.isActive = True
    PcObject.save(provider_object.provider)
    saveCounts()
    provider_object.updateObjects()

    for countName in ['updatedObjects',
                      'createdObjects',
                      'checkedObjects',
                      'erroredObjects',
                      'createdThumbs',
                      'updatedThumbs',
                      'checkedThumbs',
                      'erroredThumbs']:
        assert getattr(provider_object, countName) == counts[countName]
        del counts[countName]
    assertCreatedCounts(**counts)


def activate_provider(provider_classname: str) -> Provider:
    provider = get_provider_by_local_class(provider_classname)
    provider.isActive = True
    provider.enabledForPro = True
    PcObject.save(provider)
    return provider


def create_providable_info(model_name: Model = Product,
                           id_at_providers: str = '1',
                           date_modified: datetime = None) -> ProvidableInfo:
    providable_info = ProvidableInfo()
    providable_info.type = model_name
    providable_info.id_at_providers = id_at_providers
    if date_modified:
        providable_info.date_modified_at_provider = date_modified
    else:
        providable_info.date_modified_at_provider = datetime.utcnow()
    return providable_info


def assert_iterator_is_empty(custom_iterator: iter):
    with pytest.raises(StopIteration):
        next(custom_iterator)


saved_counts = {}