from django.test import TestCase
from .path_convertor import UnicodeSlug
from web.models import Teacher, Group
from django.shortcuts import reverse

class UnicodeSlugTests(TestCase):
    def test_normal_named_groups_to_slug(self):
        slug = UnicodeSlug()
        value = slug.to_url('آزمایشگاه پایگاه داده استاد سلیمانی')
        self.assertEqual(value, 'آزمایشگاه-پایگاه-داده-استاد-سلیمانی',)

        value = slug.to_url('فیزیک ۲')
        self.assertEqual(value, 'فیزیک-۲')

        value = slug.to_url('-----پایگاه داده+++++سلیمانی ۲')
        self.assertEqual(value, '-پایگاه-دادهسلیمانی-۲')

    def test_valid_to_python_format(self):
        slug = UnicodeSlug()
        valid_names = [
            'آزمایشگاه-پایگاه-داده-استاد-سلیمانی',
            'آزمایشگاه-پایگاه-داده-استاد-سلیمانی-۲',
            'آزمایشگاه-پایگاه-داده-استاد-سلیمانی-2',
            'فیزیک-۲-استاد-رحیم-فر',
            'فیزیک-2-استاد-اسلامی',
            'آز-مدار-منطقی-استاد-وردی',
            'ریاضی-۲-استاد-نشاط',
            'کنترل-خطی-و-vlsi-استاد-خیاطی',
        ]
        for text in valid_names:
            self.assertEqual(slug.to_python(text), text)

    def test_invalid_to_python_format(self):
        slug = UnicodeSlug()
        invalid_names = [
            'ازمایشگاه فیزیک',
            '۲۲۲۲۲ فیزیک ۲۲۲۲',
            'فیزیک-۲',
            'فیزیک-۲-استاد',
            'فیزیک++++استاد+++رحیمی',
            '$$$فیزیکـ-آزمایشگاهــ!!',
            'احسان علیخانی',
            'امیرـحسین+++یعقوبیــ+ـ۰۰۹۱۲',
            'آزپایگاه ۱۳۰۴۴',
            '',
            '             ',
            '-------------------',
            '_____________________',
            '++++-asdad',
            '======---$#%^',
            '@@@',
            '!!!#$$%',
            'fizik',
            'استاد-رحیمی-فیزیک۲',
            'فیزیک۲؟-امیر-استاد-احسیم',
            'آزمایشگاه فیزیک ۲ استاد فلانی',
        ]

        for text in invalid_names:
            flag = True
            try:
                slug.to_python(text)
                flag = False
            except ValueError:
                pass
            self.assertIs(flag, True, msg=f'test failed: value={text} | (values must be invalid)')


class TeacherModelTests(TestCase):

    def test_to_string(self):
        teacher = Teacher.objects.create(name='اسلامی', email='rng@gmail.com')
        self.assertEqual(teacher.__str__(), 'استاد اسلامی')

        teacher = Teacher.objects.create(name='فاطمه رزاقی', email='rng@gmail.com')
        self.assertEqual(teacher.__str__(), 'استاد فاطمه رزاقی')


class GroupModelTests(TestCase):
    def setUp(self):
        self.teacher1 = Teacher.objects.create(name='اسلامی', email='rng@gmail.com')
        self.teacher2 = Teacher.objects.create(name='احسانی', email='rig@gmail.com')

    def test_generated_unique_slug(self):
        group1 = Group.objects.create(title='آزمایشگاه فیزیک کوانتوم',
                                      chat_id=1, members=10, admin_id=1,
                                      admin_username='@username',
                                      teacher=self.teacher1, category='T',
                                      active=True)

        self.assertEqual(group1.slug, 'آزمایشگاه-فیزیک-کوانتوم-استاد-اسلامی')
        self.assertEqual(group1._generate_unique_slug(), 'آزمایشگاه-فیزیک-کوانتوم-استاد-اسلامی-1')

        group1 = Group.objects.create(title='آزمایشگاه فیزیک کوانتوم',
                                      chat_id=2, members=11, admin_id=2,
                                      admin_username='@username',
                                      teacher=self.teacher1, category='T',
                                      active=True)
        self.assertEqual(group1.slug, 'آزمایشگاه-فیزیک-کوانتوم-استاد-اسلامی-1')
        self.assertEqual(group1._generate_unique_slug(), 'آزمایشگاه-فیزیک-کوانتوم-استاد-اسلامی-2')


# class IndexViewTest(TestCase):
#     def setUp(self):
#         self.teacher1 = Teacher.objects.create(name='اسلامی', email='rng@gmail.com')
#         self.group1 = Group.objects.create(title='آزمایشگاه فیزیک کوانتوم',
#                                       chat_id=1, members=10, admin_id=1,
#                                       admin_username='@username',
#                                       teacher=self.teacher1, category='T',
#                                       active=True)
#
#     def test_sample(self):
#         url = reverse('get_group_link', kwargs={'slug': str(self.group1.slug)})
#         resp = self.client.get(url)
#         print(resp)