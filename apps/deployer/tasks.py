from celery.task import task
from deploy import fabfile

from utils import send_templated_email
from fabric.state import output
from apps.deployer.models import Deploy

import fabric
import logging
import traceback

import re

logger = logging.getLogger('deployer')
sha_re = re.compile(r'[0-9a-f]{40}')

@task
def deploy(deploy_id, user, password, deploy_type, env):
    # output['status'] = False
    deploy = Deploy.objects.get(id=deploy_id)
    deploy.update_status('started')

    successful = False

    try:
        fabfile.env.no_colors = True
        fabfile.env.no_output = True
        fabfile.dev(user.username)
        fabfile.env.password = password

        deploy_type = int(deploy_type)

        if deploy_type == Deploy.TYPE_IDS['Web+Static']:
            fabfile.update()
        elif deploy_type == Deploy.TYPE_IDS['Web']:
            fabfile.update_web()
        elif deploy_type == Deploy.TYPE_IDS['Static']:
            fabfile.update_static()
        else:
            raise TypeError("Could not find a type %s", deploy_type)
    except Exception, e:
        logger.error("Something wrong happened", e)
        out = traceback.format_exc()
    else:
        out = ''.join(fabfile._out_log.readlines())
        successful = True
    finally:
        fabric.network.disconnect_all()

    deploy.output = out
    deploy.commit = fabfile.show_commit()

    if successful:
        deploy.update_status('finished successfuly')
    else:
        deploy.update_status('finished with error')

    context = {
        'output': out,
        'user': user.username
    }

    subject = 'Deploy is done' if successful else 'Deploy finished with error :('

    send_templated_email(user, subject,
                         'deployer/deploy_done.html',
                         context, fail_silently=False)
