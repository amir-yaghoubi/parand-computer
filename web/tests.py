from datetime import datetime

from django.test import TestCase

from utils.path_convertor import GroupSlug
from web.models import Teacher, Group, PendingGroup


class UnicodeSlugTests(TestCase):
    def test_normal_named_groups_to_slug(self):
        slug = GroupSlug()
        value = slug.to_url('آزمایشگاه پایگاه داده استاد سلیمانی')
        self.assertEqual(value, 'آزمایشگاه-پایگاه-داده-استاد-سلیمانی',)

        value = slug.to_url('فیزیک ۲')
        self.assertEqual(value, 'فیزیک-۲')

        value = slug.to_url('-----پایگاه داده+++++سلیمانی ۲')
        self.assertEqual(value, '-پایگاه-دادهسلیمانی-۲')

    def test_valid_to_python_format(self):
        slug = GroupSlug()
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
        slug = GroupSlug()
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

    def test_to_string(self):
        group = Group.objects.create(title='آزمایشگاهوم',
                             chat_id=67, members=10, admin_id=1,
                             admin_username='@username',
                             teacher=self.teacher1, category='T', created_date=datetime.now(),
                             active=True)
        self.assertEqual(str(group), f'{group.title}-{group.get_category_display()}')


class PendingGroupModelTests(TestCase):
    def test_to_string(self):
        pending_gp = PendingGroup.objects.create(chat_id=100, admin_id=100,
                                                 admin_username='@Amir',
                                                 title='ریزپردازنده')
        self.assertEqual(str(pending_gp), f'گروه {pending_gp.title} ساخته شده توسط {pending_gp.admin_username}')
