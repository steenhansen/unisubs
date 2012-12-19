# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.utils.translation import ugettext as _

from messages.forms import SendMessageForm
from messages.models import Message
from messages.tasks import send_new_message_notification

class MessagesApiClass(object):
    def remove(self, message_id, user):
        if not user.is_authenticated():
            return {'error': _('You should be authenticated.')}

        try:
            try:
                msg = Message.objects.for_user(user).get(pk=message_id)
            except Message.DoesNotExist:
                msg = Message.objects.for_author(user).get(pk=message_id)
        except Message.DoesNotExist:
            return {'error': _('Message does not exist.')}

        msg.delete_for_user(user)

        return {}

    def mark_as_read(self, message_id, user):
        if not user.is_authenticated():
            return {'error': _('You should be authenticated.')}

        Message.objects.filter(pk=message_id, user=user).update(read=True)

        return {}

    def mark_all_read(self, user):
        if not user.is_authenticated():
            return {'error': _('You should be authenticated.')}

        Message.objects.filter(user=user).update(read=True)

        return {}

    def send(self, rdata, user):
        if not user.is_authenticated():
            return {'error': _('You should be authenticated.')}

        form = SendMessageForm(user, rdata)
        if form.is_valid():
            m = form.save()
            
            send_new_message_notification.delay(m.pk)
        else:
            return dict(errors=form.get_errors())

        return {}

