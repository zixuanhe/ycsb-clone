from datetime import datetime, timedelta
from fabric.context_managers import settings, hide
from conf import hosts, databases, workloads

def base_time(time=None, round_sec=60, tz = hosts.timezone):
    """
    Get the next timestamp rounded to round_sec seconds
    the function returns some future time rounded accordingly
    to round_sec parameter.
    Examples: 2:22:29 -> 2:23:00
              2:22:31 -> 2:24:00
    """
    if time is None: time = datetime.now(tz)
    begin = time.min.replace(tzinfo=tz) # long time ago
    seconds = (time - begin).seconds
    rounding = (seconds + round_sec * 1.5) // round_sec * round_sec
    return time + timedelta(0, rounding-seconds, -time.microsecond)

def almost_nothing():
    return settings(hide('running', 'warnings', 'stdout', 'stderr'), warn_only=True)

def get_db(database):
    if not databases.databases.has_key(database):
        raise Exception("unconfigured database '%s'" % database)
    return databases.databases[database]

def get_workload(workload):
    if not workloads.workloads.has_key(workload):
        raise Exception("unconfigured workload '%s'" % workload)
    return workloads.workloads[workload]

def get_outfilename(databasename, workloadname, extension, the_time, target=None):
    the_time_str = the_time.strftime('%Y-%m-%d_%H-%M')
    if target is None:
        return '%s_%s_%s.%s' % (the_time_str, databasename, workloadname, extension)
    else:
        return '%s_%s_%s_%s.%s' % (the_time_str, databasename, workloadname, str(target), extension)

def _at(cmd, time=base_time()):
    return 'echo "%s" | at %s today' % (cmd, time.strftime('%H:%M'))
