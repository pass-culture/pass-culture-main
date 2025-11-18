import os
import re


# The goal of this test is to ensure that
# all the celery tasks are properly registered
# in the celery worker
def test_tasks_are_properly_registered():
    tasks_module_that_should_be_imported = []
    # list modules that should be imported
    # based on their usage of `@celery_async_task`
    # decorator
    for root, _, fnames in os.walk("./src/pcapi"):
        for fname in fnames:
            if fname.endswith(".py"):
                task_file = os.path.join(root, fname)
                with open(task_file, "r") as file:
                    file_content = file.read()
                if re.search(r"@celery_async_task\(", file_content):
                    module = task_file.replace("./src/", "").replace(".py", "").replace("/", ".")
                    tasks_module_that_should_be_imported.append(module)

    with open("./src/pcapi/celery_tasks/celery_worker.py", "r") as file:
        celery_worker_file_content = file.read()

    missing_tasks_import = []
    for task_module in tasks_module_that_should_be_imported:
        if task_module not in celery_worker_file_content:
            missing_tasks_import.append(task_module)

    assert len(missing_tasks_import) == 0, (
        f"The following modules should be imported in `pcapi.celery_tasks.celery_worker`: {' '.join(missing_tasks_import)}"
    )
