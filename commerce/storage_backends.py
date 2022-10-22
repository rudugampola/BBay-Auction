from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = True


class FileStorage(S3Boto3Storage):
    location = 'graphs'
    file_overwrite = True
