import socket


def get_deployment():
    """Return the name of the Kubernetes deployment, based on the
    hostname of the pod.

    Outside a Kubernetes pod, return the hostname (or a part of it).
    """
    # pod names look like "{env}-pcapi-{pod-kind}-{id1}-{id2}",
    # where `{pod-kind}` may contain dashes.
    name = socket.gethostname()
    try:
        return name.split("-", 2)[-1].rsplit("-", 2)[0]
    except IndexError:  # not a pod, return full name
        return name
