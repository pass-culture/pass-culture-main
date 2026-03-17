import functools
import os
import sys
import typing
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from threading import local
from traceback import print_exc

import psycopg2


DB_URL = "postgresql://localhost:5432/testing"
JOB_DIRECTORY = "jobs"
WOKERS_COUNT = 4

thread_storage = local()


@dataclass(frozen=True, slots=True)
class Job:
    name: str
    sql: str | None
    python: str | None
    dependencies: frozenset[str]


class EndWorkerObject:
    pass


def db_connection(function: typing.Callable) -> typing.Callable:
    @functools.wraps
    def wrapper(code: str) -> None:
        db = psycopg2.connect(DB_URL)
        try:
            return function(code, db=db)
        finally:
            db.close()

    return wrapper


@db_connection
def execute_python(python_code: str, *, db: psycopg2.extensions.connection) -> None:
    exec(python_code, locals={"db": db})


@db_connection
def execute_sql(sql_code: str, *, db: psycopg2.extensions.connection) -> None:
    cursor = db.cursor()
    cursor.execute(sql_code)
    db.commit()


def worker(todo: Queue, results: Queue) -> None:
    """a worker thread"""
    print("starting worker")
    while True:
        try:
            job = todo.get()
            if isinstance(job, EndWorkerObject):
                print("exiting worker")
                break
            print("job %s starting" % job.name)
            if job.python:
                execute_python(job.python)
            if job.sql:
                execute_sql(job.sql)

            print("job %s success" % job.name)
            results.put((job, True))
        except Exception:
            print_exc()
            print("job %s failed" % job.name)

            results.put((job, False))


def clean_exit(exit_code: int = 0) -> None:
    print("starting clean exit" % thread_storage.threads)
    if thread_storage.threads:
        for i in range(len(thread_storage.threads)):
            thread_storage.todo.put(EndWorkerObject())
        for thread in thread_storage.threads:
            thread.join()
    sys.exit(exit_code)


def get_code_and_dependancies(file_path: str) -> tuple[str, str, frozenset]:
    code = ""
    dependencies = []
    extension = file_path.split(".")[-1]
    if extension == "sql":
        dependencies_header = "-- meta: dependencies="
    elif extension == "py":
        dependencies_header = "# meta: dependencies="
    else:
        return "", extension, frozenset()

    with open(file_path) as fp:
        while line := fp.readline():
            if line.startswith(dependencies_header):
                dependencies = [dep.strip() for dep in line[len(dependencies_header) : -1].split(",") if dep.strip()]
            else:
                code += line

    return code, extension, frozenset(dependencies)


def get_jobs_dict() -> dict:
    print("loading jobs")
    jobs = {}
    for filename in os.listdir(JOB_DIRECTORY):
        file_path = JOB_DIRECTORY + "/" + filename
        if filename.startswith("."):
            print(f"ignoring {filename})")
            continue

        filename_components = filename.split(".")
        if len(filename_components) != 2:
            print(f"ignoring {filename})")
            continue

        name = filename_components[0]
        code, extension, dependencies = get_code_and_dependancies(file_path)

        if not code:
            print(f"ignoring {filename})")
            continue

        jobs[name] = Job(
            name=name,
            sql=code if extension == "sql" else None,
            python=code if extension == "py" else None,
            dependencies=dependencies,
        )
    return jobs


def handle_dependencies(pending: list, finished: set, todo: Queue, last_finished: Job) -> None:
    finished.add(last_finished.name)
    for i in range(len(pending)):
        job = pending[i]
        if last_finished.name in job.dependencies:
            for dependence in job.dependencies:
                if dependence not in finished:
                    break
            else:
                pending.pop(i)
                todo.put(job)


def main() -> None:
    print("setup")
    thread_storage.todo = Queue()
    thread_storage.results = Queue()
    thread_storage.threads = []

    jobs = get_jobs_dict()

    print("starting worker threads threads")
    # setup worker
    for i in range(WOKERS_COUNT):
        thread_storage.threads.append(
            Thread(
                target=worker,
                kwargs={
                    "todo": thread_storage.todo,
                    "results": thread_storage.results,
                },
            )
        )
        thread_storage.threads[-1].start()

    # setup jobs
    pending = []
    for job in jobs.values():
        if not job.dependencies:
            thread_storage.todo.put(job)
        else:
            pending.append(job)
    finished: set[str] = set()

    # manage results
    while True:
        if len(finished) == len(jobs):
            print("all done")
            clean_exit(0)
        res = thread_storage.results.get()
        job, result = res
        if not result:
            print("error on job %s exiting" % job.name)
            clean_exit(2)

        handle_dependencies(
            pending=pending,
            finished=finished,
            todo=thread_storage.todo,
            last_finished=job,
        )


if __name__ == "__main__":
    main()
