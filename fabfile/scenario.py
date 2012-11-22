
from fabric.api import *
from fabric.colors import green, blue, red

from conf import hosts, workloads, databases

# the scenario to execute and stop servers remotely
# and control network on those machines to simulate splits,
# delays and packet losses
