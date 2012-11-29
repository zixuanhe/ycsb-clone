from fabric.api import env
import pytz

env.user = 'root'
env.password = 'thumbtack'

env.show = ['debug']

env.roledefs = {
    'client': ['c1.citrusleaf.local', 'c2.citrusleaf.local', 'c3.citrusleaf.local', 'c4.citrusleaf.local'],
    'server': ['e1.citrusleaf.local', 'e2.citrusleaf.local', 'e3.citrusleaf.local', 'e4.citrusleaf.local'],
}

timezone = pytz.timezone('US/Pacific')
