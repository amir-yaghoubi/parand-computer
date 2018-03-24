from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.views.generic import ListView

from telegram_bot.actions import get_group_link
from .models import Group


class IndexPage(ListView):
    queryset = Group.objects.filter(active=True).order_by('-title').all()
    template_name = 'web/index.html'
    context_object_name = 'groups'

    def _group_by_category(self, groups):
        azmayeshgah = []
        takhasosi = []
        other = []
        for gp in groups:
            info = {'title': gp.title, 'teacher': str(gp.teacher), 'link': gp.link, 'slug': gp.slug}
            if gp.category == 'A':
                azmayeshgah.append(info)
            elif gp.category == 'T':
                takhasosi.append(info)
            else:
                other.append(info)

        return {
            'azmayeshgah': azmayeshgah,
            'takhasosi': takhasosi,
            'other': other
        }

    def get_context_data(self, **kwargs):
        # دریافت لیست گروه ها
        context = super().get_context_data(**kwargs)
        # گروه بندی بر گروه‌ها و تغییر کانتکست
        context['groups'] = self._group_by_category(context['groups'])
        return context


def about(request):
    return render(request, 'web/index.html', {})


def help_view(request):
    return render(request, 'web/index.html', {})