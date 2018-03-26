import re
from django.utils.text import slugify


class NormalSlug:
    regex = '[\w-]{1,}'

    def to_python(self, value):
        math_result = re.fullmatch(self.regex, value, flags=re.UNICODE)
        # اگه مقدار داده شده با فرمت ما مطابقت می‌کرد
        if math_result is not None:
            return value
        raise ValueError('Does not match with regex, value:{}'.format(value))

    def to_url(self, value):
        return slugify(value, allow_unicode=True)

    @staticmethod
    def slug_it(**kwargs):
        """
        :param kwargs: 'title' field is required
        :return: slug of your group title
        """
        if kwargs['title'] is None:
            raise ValueError('required keyword: title')
        return slugify(kwargs['title'], allow_unicode=True)


class GroupSlug(NormalSlug):
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

    @staticmethod
    def slug_it(**kwargs):
        """
        :param kwargs: title and teacher keywords are required
        :return: slug of your group
        """
        if kwargs['title'] is None or kwargs['teacher'] is None:
            raise ValueError('required keywords: title, teacher')
        return slugify(kwargs['title'] + ' ' + str(kwargs['teacher']), allow_unicode=True)

