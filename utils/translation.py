# -*- coding: utf-8 -*-
import time

from django.conf import settings
from django.core.cache import cache
from django.utils import simplejson as json
from django.utils.http import cookie_date
from django.utils.translation import (
    get_language, get_language_info, ugettext as _
)
from django.utils.translation.trans_real import parse_accept_lang_header

from unilangs import get_language_name_mapping, LanguageCode


# A set of all language codes we support.
SUPPORTED_LANGUAGE_CODES = set(get_language_name_mapping('unisubs').keys())


def _only_supported_languages(language_codes):
    """Filter the given list of language codes to contain only codes we support."""

    # TODO: Figure out the codec issue here.
    return [code for code in language_codes if code in SUPPORTED_LANGUAGE_CODES]


def get_language_choices(with_empty=False):
    """Return a list of language code choices labeled appropriately."""

    cache_key = 'simple-langs-cache-%s' % get_language()
    languages = cache.get(cache_key)

    if not languages:
        languages = []

        for code, name in get_language_name_mapping('unisubs').items():
            languages.append((code, _(name)))

        languages.sort(key=lambda item: item[1])
        cache.set(cache_key, languages, 60*60)

    if with_empty:
        languages = [('', '---------')] + languages

    return languages

def get_language_label(code):
    """Return the translated, human-readable label for the given language code."""
    lc = LanguageCode(code, 'unisubs')
    return u'%s' % _(lc.name())


def get_user_languages_from_request(request):
    """Return a list of our best guess at languages that request.user speaks."""
    languages = []

    if request.user.is_authenticated():
        languages = [l.language for l in request.user.get_languages()]

    if not languages:
        languages = languages_from_request(request)

    return _only_supported_languages(languages)

def set_user_languages_to_cookie(response, languages):
    max_age = 60*60*24
    response.set_cookie(
        settings.USER_LANGUAGES_COOKIE_NAME,
        json.dumps(languages),
        max_age=max_age,
        expires=cookie_date(time.time() + max_age))

def get_user_languages_from_cookie(request):
    try:
        langs = json.loads(request.COOKIES.get(settings.USER_LANGUAGES_COOKIE_NAME, '[]'))
        return _only_supported_languages(langs)
    except (TypeError, ValueError):
        return []


def languages_from_request(request):
    languages = []

    for l in get_user_languages_from_cookie(request):
        if not l in languages:
            languages.append(l)

    if not languages:
        trans_lang = get_language()
        if not trans_lang in languages:
            languages.append(trans_lang)

        if hasattr(request, 'session'):
            lang_code = request.session.get('django_language', None)
            if lang_code is not None and not lang_code in languages:
                languages.append(lang_code)

        cookie_lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if cookie_lang_code and not cookie_lang_code in languages:
            languages.append(cookie_lang_code)

        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for lang, val in parse_accept_lang_header(accept):
            if lang and lang != '*' and not lang in languages:
                languages.append(lang)

    return _only_supported_languages(languages)

def languages_with_labels(langs):
    """Return a dict of language codes to language labels for the given seq of codes.

    These codes must be in the internal unisubs format.

    The labels will be in the standard label format.

    """
    return dict([code, get_language_label(code)] for code in langs)


def is_rtl(lang):
    # there are languages on our system that are not on django.
    # so, let's find and return the right value here:
    if lang in ('arq', 'pnb',):
        return True

    # Forcing Azerbaijani to be a left-to-right language.
    # For: https://unisubs.sifterapp.com/projects/12298/issues/753035/comments 
    if lang == 'az':
        return False

    try:
        return get_language_info(lang)['bidi']
    except KeyError:
        return False
