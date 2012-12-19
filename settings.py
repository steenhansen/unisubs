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

# Django settings for unisubs project.
import os, sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DEFAULT_PROTOCOL  = 'http'

def rel(*x):
    return os.path.join(PROJECT_ROOT, *x)

# Rebuild the language dicts to support more languages.
from django.conf import global_settings
from unilangs import get_language_code_mapping

# We use a custom format for our language labels:
# Translated Language Name (Native Name)
#
# For example: if you are an English user you'll see something like:
# French (Français)
language_choices = [(code,
                     u'%s' % lc.name())
                    for code, lc in get_language_code_mapping('unisubs').items()]

global_settings.LANGUAGES = ALL_LANGUAGES = language_choices

# Languages representing metadata
METADATA_LANGUAGES = (
    ('meta-tw', 'Metadata: Twitter'),
    ('meta-geo', 'Metadata: Geo'),
    ('meta-wiki', 'Metadata: Wikipedia'),
)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

PISTON_EMAIL_ERRORS = True
PISTON_DISPLAY_ERRORS = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

ALARM_EMAIL = None
MANAGERS = ADMINS

P3P_COMPACT = 'CP="CURa ADMa DEVa OUR IND DSP CAO COR"'

DEFAULT_FROM_EMAIL = '"Amara" <feedback@universalsubtitles.org>'
WIDGET_LOG_EMAIL = 'widget-logs@universalsubtitles.org'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': rel('unisubs.sqlite3'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# 'embed{0}.js'.format(EMBED_JS_VERSION) gives the current embed script file name.
EMBED_JS_VERSION = ''
PREVIOUS_EMBED_JS_VERSIONS = []

CSS_USE_COMPILED = True

USE_BUNDLED_MEDIA = not DEBUG

COMPRESS_YUI_BINARY = "java -jar ./css-compression/yuicompressor-2.4.6.jar"
COMPRESS_OUTPUT_DIRNAME = "static-cache"


USER_LANGUAGES_COOKIE_NAME = 'unisub-languages-cookie'

# paths provided relative to media/js
JS_CORE = \
    ['js/unisubs.js', 
     'js/rpc.js',
     'js/clippy.js',
     'js/flash.js',
     'js/spinner.js',
     'js/sliderbase.js',
     'js/closingwindow.js',
     'js/loadingdom.js',
     'js/tracker.js',
     'js/style.js',
     'js/html/markdown.js',
     'js/messaging/simplemessage.js',
     'js/player/video.js',
     'js/player/captionview.js',
     'js/widget/usersettings.js',
     'js/player/abstractvideoplayer.js',
     'js/player/flashvideoplayer.js',
     'js/player/html5mediaplayer.js',
     'js/player/html5videoplayer.js',
     'js/player/html5audioplayer.js',
     'js/player/youtubevideoplayer.js',
     'js/player/ytiframevideoplayer.js',
     'js/player/youtubebasemixin.js',
     'js/player/jwvideoplayer.js',
     'js/player/flvvideoplayer.js',
     'js/player/flashaudioplayer.js',
     'js/player/mediasource.js',
     'js/player/mp3source.js',
     'js/player/html5videosource.js',
     'js/player/youtubevideosource.js',
     'js/player/ytiframevideosource.js',
     'js/player/brightcovevideosource.js',
     'js/player/brightcovevideoplayer.js',
     'js/player/flvvideosource.js',
     'js/player/bliptvplaceholder.js',
     'js/player/bliptvvideoplayer.js',
     'js/player/bliptvvideosource.js',
     'js/player/controlledvideoplayer.js',
     'js/player/vimeovideosource.js',
     'js/player/vimeovideoplayer.js',
     'js/player/wistiavideosource.js',
     'js/player/wistiavideoplayer.js',
     'js/player/dailymotionvideosource.js',
     'js/player/dailymotionvideoplayer.js',
     'js/startdialog/model.js',
     'js/startdialog/videolanguage.js',
     'js/startdialog/videolanguages.js',
     'js/startdialog/tolanguage.js',
     'js/startdialog/tolanguages.js',
     'js/startdialog/dialog.js',
     'js/streamer/streambox.js', 
     'js/streamer/streamboxsearch.js', 
     'js/streamer/streamsub.js', 
     'js/streamer/streamervideotab.js', 
     'js/streamer/streamerdecorator.js', 
     'js/widget/videotab.js',
     'js/widget/hangingvideotab.js',
     'js/widget/subtitle/editablecaption.js',
     "js/widget/subtitle/editablecaptionset.js",
     'js/widget/logindialog.js',
     'js/widget/howtovideopanel.js',
     'js/widget/guidelinespanel.js',
     'js/widget/dialog.js',
     'js/widget/captionmanager.js',
     'js/widget/rightpanel.js',
     'js/widget/basestate.js',
     'js/widget/subtitlestate.js',
     'js/widget/dropdowncontents.js',
     'js/widget/playcontroller.js',
     'js/widget/subtitlecontroller.js',
     'js/widget/subtitledialogopener.js',
     'js/widget/opendialogargs.js',
     'js/widget/dropdown.js',
     'js/widget/resumeeditingrecord.js',
     'js/widget/resumedialog.js',
     'js/widget/subtitle/savedsubtitles.js',
     'js/widget/play/manager.js',
     'js/widget/widgetcontroller.js',
     'js/widget/widget.js'
]

JS_DIALOG = \
    ['js/subtracker.js',
     'js/srtwriter.js',
     'js/widget/unsavedwarning.js',
     'js/widget/emptysubswarningdialog.js',
     'js/widget/confirmdialog.js',
     'js/widget/droplockdialog.js',
     'js/finishfaildialog/dialog.js',
     'js/finishfaildialog/errorpanel.js',
     'js/finishfaildialog/reattemptuploadpanel.js',
     'js/finishfaildialog/copydialog.js',
     'js/widget/editmetadata/dialog.js',
     'js/widget/editmetadata/panel.js',
     'js/widget/editmetadata/editmetadatarightpanel.js',
     'js/widget/subtitle/dialog.js',
     'js/widget/subtitle/msservermodel.js',
     'js/widget/subtitle/subtitlewidget.js',
     'js/widget/subtitle/addsubtitlewidget.js',
     'js/widget/subtitle/subtitlelist.js',
     'js/widget/subtitle/transcribeentry.js',
     'js/widget/subtitle/transcribepanel.js',
     'js/widget/subtitle/transcriberightpanel.js',
     'js/widget/subtitle/syncpanel.js',
     'js/widget/subtitle/reviewpanel.js',
     'js/widget/subtitle/reviewrightpanel.js',
     'js/widget/subtitle/sharepanel.js',
     'js/widget/subtitle/completeddialog.js',
     'js/widget/subtitle/editpanel.js',
     'js/widget/subtitle/onsaveddialog.js',
     'js/widget/subtitle/editrightpanel.js',
     'js/widget/subtitle/bottomfinishedpanel.js',
     'js/widget/subtitle/logger.js',
     'js/widget/timeline/timerow.js',
     'js/widget/timeline/timerowul.js',
     'js/widget/timeline/timelinesub.js',
     'js/widget/timeline/timelinesubs.js',
     'js/widget/timeline/timelineinner.js',
     'js/widget/timeline/timeline.js',
     'js/widget/timeline/subtitle.js',
     'js/widget/timeline/subtitleset.js',
     'js/widget/controls/bufferedbar.js',
     'js/widget/controls/playpause.js',
     'js/widget/controls/progressbar.js',
     'js/widget/controls/progressslider.js',
     'js/widget/controls/timespan.js',
     'js/widget/controls/videocontrols.js',
     'js/widget/controls/volumecontrol.js',
     'js/widget/controls/volumeslider.js',
     'js/widget/translate/bingtranslator.js',
     'js/widget/translate/dialog.js',
     'js/widget/translate/translationpanel.js',
     'js/widget/translate/translationlist.js',
     'js/widget/translate/translationwidget.js',
     'js/widget/translate/descriptiontranslationwidget.js',
     'js/widget/translate/translationrightpanel.js',
     'js/widget/translate/forkdialog.js',
     'js/widget/translate/titletranslationwidget.js']

JS_OFFSITE = list(JS_CORE)
JS_OFFSITE.append('js/widget/crossdomainembed.js')

JS_ONSITE = list(JS_CORE)
JS_ONSITE.extend(
    ['js/srtwriter.js',
     'js/widget/samedomainembed.js',
     "js/widget/api/servermodel.js",
     'js/widget/controls/bufferedbar.js',
     'js/widget/controls/playpause.js',
     'js/widget/controls/progressbar.js',
     'js/widget/controls/progressslider.js',
     'js/widget/controls/timespan.js',
     'js/widget/controls/videocontrols.js',
     'js/widget/controls/volumecontrol.js',
     'js/widget/controls/volumeslider.js',
     "js/widget/api/api.js"])

JS_WIDGETIZER_CORE = list(JS_CORE)
JS_WIDGETIZER_CORE.extend([
    "js/widget/widgetdecorator.js",
    "js/widgetizer/videoplayermaker.js",
    "js/widgetizer/widgetizer.js",
    "js/widgetizer/youtube.js",
    "js/widgetizer/html5.js",
    "js/widgetizer/jwplayer.js",
    "js/widgetizer/youtubeiframe.js",
    "js/widgetizer/wistia.js",
    "js/widgetizer/soundcloud.js",
    'js/player/ooyalaplayer.js', 
    'js/player/wistiavideoplayer.js', 
    'js/player/brightcoveliteplayer.js', 
    'js/player/soundcloudplayer.js',
    'js/streamer/overlaycontroller.js'])

JS_WIDGETIZER = list(JS_WIDGETIZER_CORE)
JS_WIDGETIZER.append('js/widgetizer/dowidgetize.js')

JS_EXTENSION = list(JS_WIDGETIZER_CORE)
JS_EXTENSION.append('js/widgetizer/extension.js')

JS_API = list(JS_CORE)
JS_API.extend(JS_DIALOG)
JS_API.extend([
        "js/widget/api/servermodel.js",
        "js/widget/api/api.js"])

JS_BASE_DEPENDENCIES = [
    'js/closure-library/closure/goog/base.js',
    'js/closure-dependencies.js',
    'js/swfobject.js',
    'flowplayer/flowplayer-3.2.6.min.js',
    'src/js/third-party/amara-jquery-1.8.2.min.js',
    'src/js/dfxp/dfxp.js',
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
STATIC_ROOT = rel('media')+'/'
MEDIA_ROOT  = rel('user-data')+'/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)


MIDDLEWARE_CLASSES = (
    'middleware.ResponseTimeMiddleware',
    'middleware.StripGoogleAnalyticsCookieMiddleware',
    'utils.ajaxmiddleware.AjaxErrorMiddleware',
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'openid_consumer.middleware.OpenIDMiddleware',
    'middleware.P3PHeaderMiddleware',
    'middleware.UserUUIDMiddleware',
    'middleware.SaveUserIp',
)

ROOT_URLCONF = 'unisubs.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
   rel('templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'utils.context_processors.current_site',
    'utils.context_processors.current_commit',
    'utils.context_processors.custom',
    'utils.context_processors.user_languages',
    'utils.context_processors.run_locally',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'utils.context_processors.media',
)

INSTALLED_APPS = (
    # this needs to be first, yay for app model loading mess
    'auth',
    # django stock apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.webdesign',
    # third party apps
    'django_extensions',
    'djcelery',
    'haystack',
    'rosetta',
    'raven.contrib.django',
    'sorl.thumbnail',
    'south',
    'tastypie',
    # third party apps forked on our repo
    'localeurl',
    'openid_consumer',
    'socialauth',
    # our apps
    'accountlinker',
    'comments',
    'messages',
    'profiles',
    'search',
    'statistic',
    'streamer',
    'teams',
    'testhelpers',
    'thirdpartyaccounts',
    'unisubs', #dirty hack to fix http://code.djangoproject.com/ticket/5494 ,
    'unisubs_compressor',
    'uslogging',
    'utils',
    'videos',
    'widget',
    'subtitles',
)

# Celery settings

# import djcelery
# djcelery.setup_loader()

# For running worker use: python manage.py celeryd -E --concurrency=10 -n worker1.localhost
# Run event cather for monitoring workers: python manage.py celerycam --frequency=5.0
# This allow know are workers online or not: python manage.py celerybeat

CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_SEND_EVENTS = False
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_RESULT_BACKEND = 'redis'

BROKER_BACKEND = 'kombu_backends.amazonsqs.Transport'
BROKER_USER = AWS_ACCESS_KEY_ID = ""
BROKER_PASSWORD = AWS_SECRET_ACCESS_KEY = ""
BROKER_HOST = "localhost"
BROKER_POOL_LIMIT = 10

#################

import re
LOCALE_INDEPENDENT_PATHS = (
    re.compile('^/widget'),
    re.compile('^/api'),
    re.compile('^/api2'),
    re.compile('^/jstest'),
    re.compile('^/sitemap.*.xml'),
    re.compile('^/accountlinker/youtube-oauth-callback/'),
    re.compile('^/crossdomain.xml'),
)

#Haystack configuration
HAYSTACK_SITECONF = 'search_site'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20
SOLR_ROOT = rel('..', 'buildout', 'parts', 'solr', 'example')

# socialauth-related
OPENID_REDIRECT_NEXT = '/socialauth/openid/done/'

OPENID_SREG = {"required": "nickname, email", "optional":"postcode, country", "policy_url": ""}
OPENID_AX = [{"type_uri": "http://axschema.org/contact/email", "count": 1, "required": True, "alias": "email"},
             {"type_uri": "fullname", "count": 1 , "required": False, "alias": "fullname"}]

FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

VIMEO_API_KEY = None
VIMEO_API_SECRET = None

AUTHENTICATION_BACKENDS = (
   'auth.backends.CustomUserBackend',
   'thirdpartyaccounts.auth_backends.TwitterAuthBackend',
   'thirdpartyaccounts.auth_backends.FacebookAuthBackend',
   'auth.backends.OpenIdBackend',
   'django.contrib.auth.backends.ModelBackend',
)

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = 'profiles.Profile'
ACCOUNT_ACTIVATION_DAYS = 9999 # we are using registration only to verify emails
SESSION_COOKIE_AGE = 2419200 # 4 weeks

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_HTTPONLY = False

RECENT_ACTIVITIES_ONPAGE = 10
ACTIVITIES_ONPAGE = 20
REVISIONS_ONPAGE = 20

FEEDBACK_EMAIL = 'socmedia@pculture.org'
FEEDBACK_EMAILS = [FEEDBACK_EMAIL]
FEEDBACK_ERROR_EMAIL = 'universalsubtitles-errors@pculture.org'
FEEDBACK_SUBJECT = 'Amara Feedback'
FEEDBACK_RESPONSE_SUBJECT = 'Thanks for trying Amara'
FEEDBACK_RESPONSE_EMAIL = 'universalsubtitles@pculture.org'
FEEDBACK_RESPONSE_TEMPLATE = 'feedback_response.html'

#teams
TEAMS_ON_PAGE = 12

PROJECT_VERSION = '0.5'

EDIT_END_THRESHOLD = 120

ANONYMOUS_USER_ID = 10000

#Use on production
GOOGLE_ANALYTICS_NUMBER = 'UA-163840-22'
MIXPANEL_TOKEN = '44205f56e929f08b602ccc9b4605edc3'

try:
    from commit import LAST_COMMIT_GUID
except ImportError:
    sys.stderr.write("deploy/create_commit_file must be ran before boostrapping django")
    LAST_COMMIT_GUID = "dev/dev"

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
DEFAULT_BUCKET = ''
AWS_USER_DATA_BUCKET_NAME  = ''
USE_AMAZON_S3 = AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and DEFAULT_BUCKET


AVATAR_MAX_SIZE = 500*1024
THUMBNAILS_SIZE = (
    (100, 100),
    (50, 50),
    (120, 90),
    (240, 240)
)

EMAIL_BCC_LIST = []

CACHE_BACKEND = 'locmem://'

#for unisubs.example.com
RECAPTCHA_PUBLIC = '6LdoScUSAAAAANmmrD7ALuV6Gqncu0iJk7ks7jZ0'
RECAPTCHA_SECRET = ' 6LdoScUSAAAAALvQj3aI1dRL9mHgh85Ks2xZH1qc'

ROSETTA_EXCLUDED_APPLICATIONS = (
    'openid_consumer',
    'rosetta'
)


INTEGRATION_PATH = os.path.join(PROJECT_ROOT, 'unisubs-integration')
USE_INTEGRATION = os.path.exists(INTEGRATION_PATH)
if USE_INTEGRATION:
    sys.path.append(INTEGRATION_PATH)

if USE_INTEGRATION:
    for dirname in os.listdir(INTEGRATION_PATH):
        if os.path.isfile(os.path.join(INTEGRATION_PATH, dirname, '__init__.py')):
            INSTALLED_APPS += (dirname,)
    
    try:
        from integration_settings import *
    except ImportError:
        pass
# paths from MEDIA URL
# this needs to run after the integration player has loaded
MEDIA_BUNDLES = {

    "base": {
        "type":"css",
        "files" : (
            "css/jquery.jgrowl.css",
            "css/jquery.alerts.css",
            "css/960.css",
            "css/reset.css",
            "css/html.css", 
            "css/about_faq.css", 
            "css/breadcrumb.css", 
            "css/buttons.css",
            "css/chosen.css",
            "css/classes.css", 
            "css/forms.css",
            "css/index.css",
            "css/layout.css",
            "css/profile_pages.css", 
            "css/revision_history.css",
            "css/teams.css", 
            "css/transcripts.css", 
            "css/background.css", 
            "css/activity_stream.css", 
            "css/settings.css", 
            "css/feedback.css", 
            "css/messages.css", 
            "css/global.css", 
            "css/top_user_panel.css", 
            "css/services.css", 
            "css/solutions.css",
            "css/watch.css",
            "css/v1.css",
            "css/bootstrap.css",
          ),
        },
    "video_history":{
        "type":"css",
        "files":(
               "css/unisubs-widget.css" ,
               "css/dev.css"
         ),
        },

    "jquery-ui":{
        "type":"css",
        "files":(
               "css/jquery-ui/jquery-ui-1.8.16.custom.css",
         ),
        },

    "home":{
        "type":"css",
        "files":(
            "css/unisubs-widget.css",
         ),
        },
     "new_home":{
         "type":"css",
         "files":(
            "css/new_index.css",
             "css/unisubs-widget.css",
          ),
         },
    "widget-css":{
         "type":"css",
         "files":(
             "css/unisubs-widget.css",
          ),
        },
    "unisubs-offsite-compiled":{
        "type": "js",
        "files": JS_OFFSITE,
        },

    "unisubs-onsite-compiled":{
        "type": "js",
        "files": JS_ONSITE,
     },
    "unisubs-widgetizer":{
        "type": "js",
        "closure_deps": "js/closure-dependencies.js",
        "files": ["js/config.js"] + JS_WIDGETIZER,
        "bootloader": { 
            "template": "widget/widgetizerbootloader.js",
            "gatekeeper": "UnisubsWidgetizerLoaded",
            "render_bootloader": True
        }
    },
    "unisubs-widgetizer-sumo": {
        "type": "js",
        "closure_deps": "js/closure-dependencies.js",
        "files": ["js/config.js"] + JS_WIDGETIZER,
        "extra_defines": {"unisubs.REPORT_ANALYTICS": "false"},
        "bootloader": { 
            "template": "widget/widgetizerbootloader.js",
            "gatekeeper": "UnisubsWidgetizerLoaded",
            "render_bootloader": True
        }
    },
    "unisubs-widgetizer-debug": {
        "type": "js",
        "files": ["js/config.js" ] + JS_WIDGETIZER  ,
        "closure_deps": "js/closure-dependencies.js",
        "debug": True,
        "bootloader": { 
            "template": "widget/widgetizerbootloader.js",
            "gatekeeper": "UnisubsWidgetizerLoaded",
            "render_bootloader": True
        }
     },
    "unisubs-statwidget":{
        "type": "js",
        "closure_deps": "js/closure-stat-dependencies.js",
        "include_flash_deps": False,
        "files": [
            'js/unisubs.js',
            'js/rpc.js',
            'js/loadingdom.js',
            'js/statwidget/statwidgetconfig.js',
            'js/statwidget/statwidget.js'],
     },

    "unisubs-api":{
        "type": "js",
        "files": ["js/config.js"] + JS_API,
        "bootloader": { 
            "gatekeeper": "UnisubsApiLoaded", 
            "render_bootloader": False
        }
     },
    "js-base-dependencies":{
        "type":"js",
        "optimizations": "WHITESPACE_ONLY",
        "files": JS_BASE_DEPENDENCIES,
     },
    "js-onsite-dialog": {
        "type":"js",
        "files": ["js/config.js"]  + JS_DIALOG  ,
    },
    "site_base_js":{
        "type":"js",
        "optimizations": "WHITESPACE_ONLY",
        "files":[
              "js/jquery-1.4.3.js",
              "js/jquery-ui-1.8.16.custom.min.js",
              "js/jgrowl/jquery.jgrowl.js",
              "js/jalerts/jquery.alerts.js",
              "js/jquery.form.js",
              "js/jquery.metadata.js",
              "js/jquery.mod.js",
              "js/jquery.rpc.js",
              "js/jquery.input_replacement.min.js",
              "js/messages.js",
              "js/escape.js",
              "js/libs/chosen.jquery.min.js",
              "js/libs/chosen.ajax.jquery.js",
              "js/libs/jquery.cookie.js",
              "js/unisubs.site.js",
            ],
        "closure_deps": "",
        "include_flash_deps": False,
        },
    "js-jqueryui-datepicker":{
        "type":"js",
        "optimizations": "WHITESPACE_ONLY",
        "files":[
              "js/jquery-ui-1.8.16.custom.datepicker.min.js",
            ],
        "include_js_base_dependencies": False,
        },
    "js-testing-base":{
        "type":"js",
        "files": [
                 'js/widget/testing/stubvideoplayer.js',
                 'js/widget/testing/events.js',
                "js/subtracker.js" ,
                "js/unitofwork.js",
                "js/testing/testing.js",
                "js/testing/timerstub.js",
            ]
    },
    "css-teams-settings-panel":{
        "type":"css",
        "files":(
            "css/chosen.css",
            "css/unisubs-widget.css",
         ),
    },
    "js-teams":{
        "type":"js",
        "optimizations": "WHITESPACE_ONLY",
        "closure_deps": "",
        "files": (
            "js/libs/ICanHaz.js",
            "js/libs/classy.js",
            "js/libs/underscore.js",
            "js/libs/chosen.jquery.min.js",
            "js/libs/chosen.ajax.jquery.js",
            "js/jquery.mod.js",
            "js/teams/create-task.js",
         ),
        "include_js_base_dependencies": False,
        "include_flash_deps": False,
    },
    "embedder":{
        "type":"js",
        "optimizations": "SIMPLE_OPTIMIZATIONS",
        "closure_deps": "",
        "files": (
            "src/js/third-party/json2.min.js",
            'src/js/third-party/underscore.min.js',
            'src/js/third-party/zepto.min.js',
            'src/js/third-party/backbone.min.js',
            'src/js/third-party/popcorn.js',
            'src/js/embedder/popcorn.amaratranscript.js',
            'src/js/embedder/popcorn.amarasubtitle.js',
            'src/js/embedder/conf.js',
            'src/js/embedder/embedder.js'
        ),
        "include_js_base_dependencies": False,
        "include_flash_deps": False,
        #"output": 'release/public/embedder.js',
        "ignore_closure": True,
        "release_url": True,
        "bootloader": { 
            "gatekeeper": "_amaraEmbedderLoaded", 
        }

    },
    "embedder-css":{
        "type":"css",
        "files": (
            "src/css/embedder/embedder-dev.css",
        ),
        "include_js_base_dependencies": False,
        "include_flash_deps": False,
        "output": 'release/public/embedder.css',
        "release_url": True,
    },
    "debug-embed-js": {
        "type": "js",
        "optimizations": "WHITESPACE_ONLY",
        "files": JS_BASE_DEPENDENCIES + JS_OFFSITE[:-1]
    }
}


EMAIL_BACKEND = "utils.safemail.InternalOnlyBackend"
EMAIL_FILE_PATH = '/tmp/unisubs-messages'
# on staging and dev only the emails listed bellow will receive actual mail
EMAIL_NOTIFICATION_RECEIVERS = ("arthur@stimuli.com.br", "steve@stevelosh.com", "@pculture.org")
# If True will not try to load media (e.g. javascript files) from third parties.
# If you're developing and have no net access, enable this setting on your
# settings_local.py
RUN_LOCALLY = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['console', 'sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'bleach': {
            'level': 'ERROR',
            'handlers': ['null'],
            'propagate': False,
        }
    },
}


try:
    import debug_toolbar

    EVERYONE_CAN_DEBUG = False
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.timer.TimerDebugPanel',
        # 'apps.testhelpers.debug_toolbar_extra.ProfilingPanel',
        # 'apps.testhelpers.debug_toolbar_extra.HaystackDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
    )

    def custom_show_toolbar(request):
        from django.conf import settings
        can_debug = settings.EVERYONE_CAN_DEBUG or request.user.is_staff

        if can_debug:
            if '__debug__/m/' in request.path or 'debug_toolbar' in request.GET:
                return True

        return False

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
        'EXTRA_SIGNALS': [],
        'HIDE_DJANGO_SQL': False,
        'TAG': 'div',
    }
except ImportError:
    pass
