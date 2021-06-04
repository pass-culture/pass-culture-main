from pydantic import BaseModel

from pcapi.tasks.decorator import task


TEST_QUEUE = "test-cyril"


class VoidTaskPayload(BaseModel):
    banana_price: int
    chouquette_price: int


@task(TEST_QUEUE, "/void_task")
def void_task(payload: VoidTaskPayload):
    print(payload)
