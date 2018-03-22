from django.forms import ModelForm
from web.models import Group


class ApproveGroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'category', 'teacher', 'active']
