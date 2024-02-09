import pcapi.core.offers.models as offers_models
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.repository.providable_queries import insert_chunk
from pcapi.repository.providable_queries import update_chunk


def get_object_from_current_chunks(
    providable_info: ProvidableInfo, chunk_to_insert: dict, chunk_to_update: dict
) -> offers_models.Product | offers_models.Offer | offers_models.Stock | None:
    chunk_key = f"{providable_info.id_at_providers}|{providable_info.type.__name__}"
    pc_object = chunk_to_insert.get(chunk_key)
    if isinstance(pc_object, providable_info.type):
        return pc_object
    pc_object = chunk_to_update.get(chunk_key)
    if isinstance(pc_object, providable_info.type):
        return pc_object
    return None


def save_chunks(chunk_to_insert: dict[str, Model], chunk_to_update: dict[str, Model]) -> None:
    if len(chunk_to_insert) > 0:
        insert_chunk(chunk_to_insert)

    if len(chunk_to_update) > 0:
        update_chunk(chunk_to_update)
