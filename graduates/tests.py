from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from .models import GraduateDocument


class GraduateDocumentImageTests(SimpleTestCase):
    def setUp(self):
        self.model_field = GraduateDocument._meta.get_field('file')
        self.form_field = self.model_field.formfield()

    def make_image(self, name='graduate.png'):
        content = BytesIO()
        Image.new('RGB', (10, 10), color='blue').save(content, format='PNG')
        return SimpleUploadedFile(name, content.getvalue(), content_type='image/png')

    def test_accepts_a_real_image(self):
        self.assertEqual(self.form_field.clean(self.make_image()).image.format, 'PNG')

    def test_rejects_a_non_image_with_an_image_extension(self):
        fake_image = SimpleUploadedFile(
            'fake.png',
            b'not an image',
            content_type='image/png',
        )
        with self.assertRaises(ValidationError):
            self.form_field.clean(fake_image)

    def test_rejects_unsupported_image_extension(self):
        with self.assertRaises(ValidationError):
            self.model_field.run_validators(self.make_image('graduate.gif'))

    def test_rejects_an_image_larger_than_ten_megabytes(self):
        oversized_image = SimpleUploadedFile(
            'large.png',
            b'x' * (10 * 1024 * 1024 + 1),
            content_type='image/png',
        )
        with self.assertRaises(ValidationError):
            self.model_field.run_validators(oversized_image)

# Create your tests here.
