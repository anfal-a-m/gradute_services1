from pathlib import PurePosixPath

from cloudinary_storage.storage import MediaCloudinaryStorage


class GraduateMediaCloudinaryStorage(MediaCloudinaryStorage):
    """Store new images as image assets while preserving legacy documents."""

    RAW_EXTENSIONS = {'.doc', '.docx', '.pdf'}

    def _get_resource_type(self, name):
        suffix = PurePosixPath(name).suffix.lower()
        if suffix in self.RAW_EXTENSIONS:
            return 'raw'
        return 'image'
