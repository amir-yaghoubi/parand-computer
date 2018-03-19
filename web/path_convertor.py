import re
from django.utils.text import slugify


class UnicodeSlug:
    """Check if given value is in our format or not
    Example:'فیزیک-۲-استاد-رحمانی'
    * value must ends with استاد-<teacher_name>
    * between each '-' we should have at least one character (unicode character)
    """
    regex = '([\w]{1,}-)+استاد-[\w-]{3,}'

    def to_python(self, value):
        math_result = re.fullmatch(self.regex, value, flags=re.UNICODE)
        # اگه مقدار داده شده با فرمت ما مطابقت می‌کرد
        if math_result is not None:
            return value
        raise ValueError('Does not match with regex, value:{}'.format(value))

    def to_url(self, value):
        return slugify(value, allow_unicode=True)
