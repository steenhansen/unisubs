from deployer.models import Deploy
from deployer.forms import DeployAppForm

from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required

from apps.videos.templatetags.paginator import paginate

from deployer import tasks

from utils import render_to

@render_to('deployer/index.html')
@staff_member_required
def index(request):
    deploys = Deploy.objects.all().order_by('-when')
    deploys, pagination_info = paginate(deploys, 20, request.GET.get('page'))

    pagination_info['deploys'] = deploys

    return pagination_info

@render_to('deployer/deploy.html')
@staff_member_required
def deploy(request):
    if request.method == 'POST':
        form = DeployAppForm(request.POST)

        if form.is_valid():
            data = form.data
            
            deploy = Deploy(user=request.user, type=data['what_to_deploy'], env=data['environment'])
            deploy.save()

            tasks.deploy.delay(deploy.id, request.user, data['password'], 
                               data['what_to_deploy'], data['environment'])
            messages.success(request, _("Deploy request sent!"))
            return redirect(reverse("deployer:index"))
    else:
        form = DeployAppForm()

    return {'form': form}
