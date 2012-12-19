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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from babelsubs.parsers.dfxp import DFXPParser
from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.videos.tests.data import (
    get_video, make_subtitle_language, make_subtitle_version
)


class DFXPTest(TestCase):
    def _download_subs(self, subtitle_language, format):
        url = reverse("widget:download", args=[format])
        res = self.client.get(url, {
            'video_id': subtitle_language.video.video_id,
            'lang_pk': subtitle_language.pk
        })
        self.assertEqual(res.status_code, 200)
        return res.content

    def test_dfxp_serializer(self):
        video = get_video()
        sl_en = make_subtitle_language(video, 'en')
        make_subtitle_version(sl_en, [(100, 200, 'Here we go!')])

        content = self._download_subs(sl_en, 'dfxp')
        serialized = DFXPParser(content)
        subtitle_set = serialized.to_internal()

        self.assertEqual(len(subtitle_set), 1)

        start, end, content, meta = list(subtitle_set)[0]

        self.assertEqual(start, 100)
        self.assertEqual(end, 200)
        self.assertEqual(content, 'Here we go!')

