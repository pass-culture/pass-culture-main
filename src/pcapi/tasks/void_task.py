from pydantic import BaseModel

from pcapi.serialization.decorator import spectree_serialize
from pcapi.tasks.decorators import cloud_task_api
from pcapi.tasks.decorators import default_queue
from pcapi.tasks.decorators import enqueue_cloud_task


PATH = "/void_task"


class VoidTaskPayload(BaseModel):
    banana_price: int
    chouquette_price: int


@cloud_task_api.route(PATH, methods=["POST"])
@spectree_serialize()
def void_task(payload: VoidTaskPayload):
    print(payload)


def enqueue_void_task(payload: VoidTaskPayload):
    enqueue_cloud_task(default_queue, PATH, payload)
