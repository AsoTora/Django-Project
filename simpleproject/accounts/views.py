from django.shortcuts import render, redirect
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from .forms import SignUpForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():  # if the form is valid,
            user = form.save()  # a User instance is created
            login(request, user)
            return redirect('homepage')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'accounts/my_account.html'
    success_url = reverse_lazy('my_account')  # It’s prevent to occur error when URLConf is not loaded

    def get_object(self):
        return self.request.user
