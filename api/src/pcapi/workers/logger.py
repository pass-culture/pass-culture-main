from rq.job import Job


def job_extra_description(job: Job) -> dict:
    return {
        "queue": job.origin,
        "job": job.id,
        "function": job.func_name,
        "call_args": str(job.args),  # args is a reserved word for logging
        "call_kwargs": str(job.kwargs),
    }
