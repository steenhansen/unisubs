from StringIO import StringIO
from hashlib import sha1
from thread import start_new_thread
from time import time
from uuid import uuid4

from boto.s3.connection import S3Connection
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.fields.files import FieldFile
from sorl.thumbnail.base import Thumbnail
from sorl.thumbnail.main import build_thumbnail_name
from south.modelsinspector import add_introspection_rules


THUMB_SIZES = getattr(settings, 'THUMBNAILS_SIZE', ())
USE_THREADED_THUMBNAIL_CREATING = getattr(settings, 'USE_THREADED_THUMBNAIL_CREATING', False)

def create_thumbnails(obj, content, size=None, thumb_name=None):
    sizes = size and [size] or obj.field.thumb_sizes

    for size in sizes:
        img = StringIO()
        content.seek(0)
        if not isinstance(content, StringIO):
            content = StringIO(content.read(content.size))
        Thumbnail(content, size, dest=img, opts=obj.field.thumb_options)
        th_name = thumb_name or obj.build_thumbnail_name(obj.name, size)
        obj.storage.save(th_name, ContentFile(img.read()))

class S3ImageFieldFile(FieldFile):
    def thumb_url(self, w, h):
        if not self.name:
            return ''

        name = self.build_thumbnail_name(self.name, (w, h))
        if not settings.USE_AMAZON_S3 and not self.storage.exists(name) and self.storage.exists(self.name):
            create_thumbnails(self, self.storage.open(self.name), (w, h), name)
        return self.storage.url(name)

    def generate_file_name(self):
        return sha1(settings.SECRET_KEY+str(time())+str(uuid4())).hexdigest()

    def build_thumbnail_name(self, name, size, options=None):
        options = options or self.field.thumb_options
        return build_thumbnail_name(name, size, options)

    def save(self, name, content, save=True):
        ext = name.split('.')[-1]
        name = '%s.%s' % (self.generate_file_name(), ext)
        name = self.field.generate_filename(self.instance, name)
        self.name = self.storage.save(name, content)
        setattr(self.instance, self.field.name, self.name)

        # Update the filesize cache
        self._size = len(content)
        self._committed = True

        if USE_THREADED_THUMBNAIL_CREATING:
            start_new_thread(create_thumbnails, (self, content))
        else:
            create_thumbnails(self, content)

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()
    save.alters_data = True

    def delete(self, save=True):
        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)

        for size in self.field.thumb_sizes:
            name = self.build_thumbnail_name(self.name, size)
            self.storage.delete(name)

        self.name = None
        setattr(self.instance, self.field.name, self.name)

        # Delete the filesize cache
        if hasattr(self, '_size'):
            del self._size
        self._committed = False

        if save:
            self.instance.save()
    delete.alters_data = True

class S3EnabledImageField(models.ImageField):
    attr_class = S3ImageFieldFile

    def __init__(self, bucket=settings.AWS_USER_DATA_BUCKET_NAME,
                       thumb_sizes=THUMB_SIZES, thumb_options=dict(crop='smart', upscale=True),
                       verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        self.thumb_sizes = thumb_sizes
        self.thumb_options = thumb_options
        self.bucket_name = bucket

        if settings.USE_AMAZON_S3:
            self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

            if self.bucket_name == settings.AWS_USER_DATA_BUCKET_NAME:
                from utils.amazon import default_s3_store
                storage = default_s3_store
                self.bucket = storage.bucket
            else:
                from utils.amazon import S3Storage
                if not self.connection.lookup(bucket):
                    self.connection.create_bucket(bucket)
                self.bucket = self.connection.get_bucket(bucket)
                storage = S3Storage(self.bucket)

            kwargs['storage'] = storage
        super(S3EnabledImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

class S3EnabledFileField(models.FileField):
    def __init__(self, bucket=settings.AWS_USER_DATA_BUCKET_NAME, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        self.bucket_name = bucket

        if settings.USE_AMAZON_S3:
            self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

            if self.bucket_name == settings.AWS_USER_DATA_BUCKET_NAME:
                from utils.amazon import default_s3_store
                storage = default_s3_store
                self.bucket = storage.bucket
            else:
                from utils.amazon import S3Storage

                if not self.connection.lookup(bucket):
                    self.connection.create_bucket(bucket)
                self.bucket = self.connection.get_bucket(bucket)
                storage = S3Storage(self.bucket)
        super(S3EnabledFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)


add_introspection_rules([
    (
        [S3EnabledImageField, S3EnabledFileField],
        [],
        {
            "bucket": ["bucket_name", {"default": settings.AWS_USER_DATA_BUCKET_NAME}]
        },
    ),
], ["^utils\.amazon\.fields"])

add_introspection_rules([
    (
        [S3EnabledImageField],
        [],
        {
            "thumb_sizes": ["thumb_sizes", {"default": THUMB_SIZES}],
            "thumb_options": ["thumb_options", {"default": dict(crop='smart')}]
        },
    ),
], ["^utils\.amazon\.fields"])
