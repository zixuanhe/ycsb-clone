from fabric.api import env

env.user = 'root'
env.roledefs = {
    'client': ['c1.citrusleaf.local', 'c2.citrusleaf.local', 'c3.citrusleaf.local', 'c4.citrusleaf.local'],
    'server': ['r1.citrusleaf.local', 'r2.citrusleaf.local', 'r3.citrusleaf.local', 'r4.citrusleaf.local'],
}
