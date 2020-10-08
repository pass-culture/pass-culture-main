from datetime import datetime
from glob import glob
from inspect import isclass

import pytest

import pcapi.models
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import PcObject, Provider, Product
from pcapi.models.db import Model
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.utils.object_storage import STORAGE_DIR

SAVED_COUNTS = {}


def save_counts():
    for model_name in pcapi.models.__all__:
        model = getattr(pcapi.models, model_name)
        if isclass(model) \
                and issubclass(model, PcObject) \
                and model_name != 'PcObject':
            SAVED_COUNTS[model_name] = model.query.count()


def assert_created_counts(**counts):
    for model_name in counts:
        model = getattr(pcapi.models, model_name)
        all_records_count = model.query.count()
        previous_records_count = SAVED_COUNTS[model_name]
        last_created_count = all_records_count - previous_records_count
        assert last_created_count == counts[model_name], \
            'Model [%s], Actual [%s], Expected [%s]' % (model_name, last_created_count, counts[model_name])


def assert_created_thumbs():
    assert len(glob(str(STORAGE_DIR / 'thumbs' / '*'))) == 1


def provider_test(app, provider, venue_provider, **counts):
    if venue_provider is None:
        provider_object = provider()
    else:
        provider_object = provider(venue_provider)
    provider_object.provider.isActive = True
    repository.save(provider_object.provider)
    save_counts()
    provider_object.updateObjects()

    for count_name in ['updatedObjects',
                       'createdObjects',
                       'checkedObjects',
                       'erroredObjects',
                       'createdThumbs',
                       'updatedThumbs',
                       'checkedThumbs',
                       'erroredThumbs']:
        assert getattr(provider_object, count_name) == counts[count_name]
        del counts[count_name]
    assert_created_counts(**counts)


def activate_provider(provider_classname: str) -> Provider:
    provider = get_provider_by_local_class(provider_classname)
    provider.isActive = True
    provider.enabledForPro = True
    repository.save(provider)
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
