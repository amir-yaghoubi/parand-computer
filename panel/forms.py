from django import forms
from web.models import Group


class ApproveGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'category', 'teacher', 'active']


class SendMessageForm(forms.Form):
    text_message = forms.CharField(max_length=4096, min_length=4, strip=True, widget=forms.Textarea,
                                   label='پیام شما:', required=True)
