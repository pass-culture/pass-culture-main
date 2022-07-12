from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.repository.providable_queries import get_existing_object
from pcapi.repository.providable_queries import insert_chunk
from pcapi.repository.providable_queries import update_chunk


def get_existing_pc_obj(
    providable_info: ProvidableInfo, chunk_to_insert: dict, chunk_to_update: dict
) -> Model | None:  # type: ignore [valid-type]
    object_in_current_chunk = get_object_from_current_chunks(providable_info, chunk_to_insert, chunk_to_update)
    if object_in_current_chunk is None:
        return get_existing_object(providable_info.type, providable_info.id_at_providers)

    return object_in_current_chunk


def get_object_from_current_chunks(
    providable_info: ProvidableInfo, chunk_to_insert: dict, chunk_to_update: dict
) -> Model | None:  # type: ignore [valid-type]
    chunk_key = f"{providable_info.id_at_providers}|{providable_info.type.__name__}"  # type: ignore [attr-defined]
    pc_object = chunk_to_insert.get(chunk_key)
    if isinstance(pc_object, providable_info.type):
        return pc_object
    pc_object = chunk_to_update.get(chunk_key)
    if isinstance(pc_object, providable_info.type):
        return pc_object
    return None


def save_chunks(chunk_to_insert: dict[str, Model], chunk_to_update: dict[str, Model]):  # type: ignore [no-untyped-def, valid-type]
    if len(chunk_to_insert) > 0:
        insert_chunk(chunk_to_insert)

    if len(chunk_to_update) > 0:
        update_chunk(chunk_to_update)
