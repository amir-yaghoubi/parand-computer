from django.shortcuts import HttpResponseRedirect, reverse


class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        # age admin vared nashode bod enteqalesh
        # midim be safhe login.
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('panel:login'))
        else:
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
