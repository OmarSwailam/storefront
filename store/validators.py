from django.core.exceptions import ValidationError


def validate_image_size(file):
    max_size_kb = 5000
    if file.size > max_size_kb * 1024:
        raise ValidationError("Max size is 5MB")
