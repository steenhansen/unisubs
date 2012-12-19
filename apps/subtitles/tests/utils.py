# -*- coding: utf-8 -*-
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

from apps.videos.models import Video
from apps.subtitles.models import SubtitleLanguage

VIDEO_URL = 'http://youtu.be/heKK95DAKms'
VIDEO_URL_2 = 'http://youtu.be/e4MSN6IImpI'
VIDEO_URL_3 = 'http://youtu.be/i_0DXxNeaQ0'


def make_video():
    video, _ = Video.get_or_create_for_url(VIDEO_URL)
    return video

def make_video_2():
    video, _ = Video.get_or_create_for_url(VIDEO_URL_2)
    return video

def make_video_3():
    video, _ = Video.get_or_create_for_url(VIDEO_URL_3)
    return video


def make_sl(video, language_code):
    sl = SubtitleLanguage(video=video, language_code=language_code)
    sl.save()
    return sl


def refresh(m):
    return m.__class__.objects.get(id=m.id)

def versionid(version):
    return version.language_code[:1] + str(version.version_number)

def ids(vs):
    return set(versionid(v) for v in vs)

def parent_ids(version):
    return ids(version.parents.all())

def ancestor_ids(version):
    return ids(version.get_ancestors())


