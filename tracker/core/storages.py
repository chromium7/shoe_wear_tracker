from storages.backends.s3boto3 import S3Boto3Storage

from django.conf import settings


class S3ImageStorage(S3Boto3Storage):

    def get_default_settings(self) -> dict:
        default_settings = super().get_default_settings()
        if not all([settings.IMAGE_S3_ACCESS_KEY_ID, settings.IMAGE_S3_SECRET_ACCESS_KEY, settings.IMAGE_S3_BUCKET_NAME]):
            return default_settings

        default_settings['bucket_name'] = settings.IMAGE_S3_BUCKET_NAME
        default_settings['access_key'] = settings.IMAGE_S3_ACCESS_KEY_ID
        default_settings['secret_key'] = settings.IMAGE_S3_SECRET_ACCESS_KEY

        return default_settings
