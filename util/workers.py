import os
import psutil


def get_worker_connections_count(worker_kind_name, default=50):
    """
    Returns the worker connections count for the gunicorn workers.
    """
    # Check for an override via an environment variable.
    override_value = os.environ.get("WORKER_CONNECTION_COUNT_" + worker_kind_name.upper(), "")
    if override_value != "":
        return override_value

    override_value = os.environ.get("WORKER_CONNECTION_COUNT", "")
    if override_value != "":
        return override_value

    return default


def get_worker_count(worker_kind_name, multiplier=1, minimum=None, maximum=None):
    """
    Returns the number of gunicorn workers to run for the given worker kind, based on a combination
    of environment variable, multiplier, minimum (if any), and number of accessible CPU cores.
    """
    # Check for an override via environment variable.
    general_multiplier_override = int(os.environ.get("WORKER_MULTIPLIER", "-1"))
    multiplier = general_multiplier_override if general_multiplier_override != -1 else multiplier

    specific_multiplier_override = int(
        os.environ.get("WORKER_MULTIPLIER_" + worker_kind_name.upper(), "-1")
    )
    multiplier = specific_multiplier_override if specific_multiplier_override != -1 else multiplier

    minimum = minimum or multiplier
    maximum = maximum or (multiplier * multiplier)

    # Check for an override via an environment variable.
    override_value = os.environ.get("WORKER_COUNT_" + worker_kind_name.upper(), "")
    if override_value != "":
        return max(override_value, minimum)

    override_value = os.environ.get("WORKER_COUNT", "")
    if override_value != "":
        return max(override_value, minimum)

    # Load the number of CPU cores via affinity, and use that to calculate the
    # number of workers to run.
    p = psutil.Process(os.getpid())

    try:
        cpu_count = len(p.cpu_affinity())
    except AttributeError:
        # cpu_affinity isn't supported on this platform. Assume 2.
        cpu_count = 2

    return min(max(cpu_count * multiplier, minimum), maximum)
