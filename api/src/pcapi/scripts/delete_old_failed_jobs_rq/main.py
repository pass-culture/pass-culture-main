from rq.registry import FailedJobRegistry

from pcapi.workers import worker


def delete_old_failed_rq_jobs(registry: FailedJobRegistry) -> None:
    # https://python-rq.org/docs/job_registries/#removing-jobs
    print(f"Jobs in FailedJobRegistry: {registry.count}")
    for job_id in registry.get_job_ids():
        registry.remove(job_id, delete_job=True)


if __name__ == "__main__":
    dq_failed_registry = worker.default_queue.failed_job_registry
    print("Start cleaning default queue failed job registry")
    delete_old_failed_rq_jobs(dq_failed_registry)
    print("Ending cleaning default queue failed job registry")
    lq_failed_registry = worker.low_queue.failed_job_registry
    print("Start cleaning low queue failed job registry")
    delete_old_failed_rq_jobs(lq_failed_registry)
    print("Ending cleaning low queue failed job registry")
