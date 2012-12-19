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

from django import forms
from django.utils.translation import ugettext_lazy as _
from utils.translation import get_language_choices

ALL_LANGUAGES = get_language_choices()

class SearchForm(forms.Form):
    SORT_CHOICES = (
        ('score', _(u'Relevance')),
        ('languages_count', _(u'Most languages')),
        ('today_views', _(u'Views Today')),
        ('week_views', _(u'Views This Week')),
        ('month_views', _(u'Views This Month')),
        ('total_views', _(u'Total Views')),
    )
    q = forms.CharField(label=_(u'query'))
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial='score',
                             label=_(u'Sort By'))
    langs = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'Subtitled Into'),
                              help_text=_(u'Left blank for any language'), initial='')
    video_lang = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'Video In'),
                              help_text=_(u'Left blank for any language'), initial='')

    def __init__(self, *args, **kwargs):
        if 'sqs' in kwargs:
            sqs = kwargs['sqs']
            del kwargs['sqs']
        else:
            sqs = None
        super(SearchForm, self).__init__(*args, **kwargs)

        if sqs:
            facet_data = sqs.facet('video_language').facet('languages').facet_counts()
            try:
                video_langs_data = facet_data['fields']['video_language']
            except KeyError:
                video_langs_data = {}
            self.fields['video_lang'].choices = self._make_choices_from_faceting(video_langs_data)

            langs_data = facet_data['fields']['languages']
            self.fields['langs'].choices = self._make_choices_from_faceting(langs_data)
        else:
            choices = list(get_language_choices())
            choices.insert(0, ('', _('All Languages')))
            self.fields['langs'].choices = choices
            self.fields['video_lang'].choices = choices

    def get_display_views(self):
        if not hasattr(self, 'cleaned_data'):
            return

        sort = self.cleaned_data.get('sort')

        if not sort:
            return

        if sort == 'today_views':
            return 'today'
        elif sort == 'week_views':
            return 'week'
        elif sort == 'month_views':
            return 'month'
        elif sort == 'total_views':
            return 'total'

    def _make_choices_from_faceting(self, data):
        choices = []

        ALL_LANGUAGES_NAMES = dict(get_language_choices())

        for lang, val in data:
            try:
                choices.append((lang, u'%s (%s)' % (ALL_LANGUAGES_NAMES[lang], val), val))
            except KeyError:
                pass

        choices.sort(key=lambda item: item[-1], reverse=True)
        choices = list((item[0], item[1]) for item in choices)
        choices.insert(0, ('', _('All Languages')))

        return choices

    @classmethod
    def apply_query(cls, q, qs):
        clean_query = qs.query.clean(q)
        qs = qs.auto_query(q)
        if clean_query:
            qs = qs.filter_or(title=clean_query).filter(is_public=True)
        return qs

    def search_qs(self, qs):
        q = self.cleaned_data.get('q')
        ordering = self.cleaned_data.get('sort', '')
        langs = self.cleaned_data.get('langs')
        video_language = self.cleaned_data.get('video_lang')

        qs = self.apply_query(q, qs)

        #aplly filtering
        if video_language:
            qs = qs.filter(video_language_exact=video_language)

        if langs:
            qs = qs.filter(languages_exact=langs)

        if ordering:
            qs = qs.order_by('-' + ordering)
        else:
            qs = qs.order_by('-score')

        return qs

