from fabric.api import env
import pytz

env.user = 'root'
env.password = 'thumbtack'

env.show = ['debug']

env.roledefs = {
    'client': ['c1.citrusleaf.local', 'c2.citrusleaf.local', 'c3.citrusleaf.local', 'c4.citrusleaf.local'],
    'server': ['r1.citrusleaf.local', 'r2.citrusleaf.local', 'r3.citrusleaf.local', 'r5.citrusleaf.local'],
}

timezone = pytz.timezone('US/Pacific')
