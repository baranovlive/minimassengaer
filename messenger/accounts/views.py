from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView

from .models import Profile
from .forms import RegisterForm, LoginForm, EditUserNames, EditUserPhoto
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User


@login_required()
def main(request):
    context = dict()
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True)
        context['users'] = users
    else:
        user_admin = User.objects.get(is_superuser=True)
        room_name = User.objects.get(username=request.user)
        context['user_admin'] = user_admin
        context['room_name'] = room_name

    context['page'] = 1
    context['page_title'] = 'Контакты'
    return render(request, 'pwaMessenger/contacts.html', context)


@login_required()
def settings(request):
    context = {
        'page': 3,
        'page_title': 'Настройки',
    }
    return render(request, 'accounts/settings.html', context)


@permission_required('polls.can_vote')
def user_management(request):
    users = User.objects.exclude(is_superuser=True)
    context = {
        'page': 3,
        'page_title': 'Удаление пользователей',
        'users': users,
    }
    return render(request, 'accounts/user_management.html', context)


@login_required()
def personal_settings(request):
    current_user = Profile.objects.get(user__username=request.user)
    context = {
        'page': 3,
        'page_title': 'Профиль',
        'current_user': current_user,
    }
    return render(request, 'accounts/personal_settings.html', context)


@permission_required('polls.can_vote')
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return HttpResponseRedirect(reverse('accounts:user_management'))


class EditNamesView(LoginRequiredMixin, FormView):
    form_class = EditUserNames
    page_title = 'Настройки'
    template_name = 'accounts/edit_user_names.html'

    def get_context_data(self, **kwargs):
        context = super(EditNamesView, self).get_context_data(**kwargs)
        context['page'] = 3
        context['page_title'] = 'Профиль'
        return context

    def get(self, request):
        form = EditUserNames()

        return super(EditNamesView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = EditUserNames(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            current_user = User.objects.get(username=request.user)
            current_user.first_name = data['first_name']
            current_user.last_name = data['last_name']
            current_user.save()
            return HttpResponseRedirect(reverse('accounts:settings'))

        return super(EditNamesView, self).get(request, form=form)


@login_required()
def edit_user_img(request):
    data = Profile.objects.get(user__username=request.user)
    form = EditUserPhoto(instance=data)
    if request.POST:
        data = Profile.objects.get(user__username=request.user)
        form = EditUserPhoto(request.POST, request.FILES, instance=data)
        if form.is_valid():
            image = form.save(commit=False)
            image.user_id = request.user
            image.save()
            return HttpResponseRedirect(reverse('accounts:settings'))
    context = {
        'form': form,
        'page_title': 'Профиль',
    }
    return render(request, "accounts/edit_user_img.html", context)


# class EditUserImg(LoginRequiredMixin, FormView):
#     form_class = EditUserPhoto
#     page_title = 'Настройки'
#     template_name = 'accounts/edit_user_img.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(EditUserImg, self).get_context_data(**kwargs)
#         context['page'] = 3
#         context['page_title'] = 'Личные настройки'
#         return context
#
#     def get(self, request):
#         form = EditUserImg()
#         return super(EditUserImg, self).get(request, form=form)
#
#     def post(self, request, *args, **kwargs):
#         form = EditUserImg(request.POST)
#
#         if form.is_valid():
#             current_user = Profile.objects.get(user__username=request.user)
#             photo = request.FILES['photo']
#             current_user.photo = photo
#             current_user.save()
#             return HttpResponseRedirect(reverse('accounts:settings'))
#
#         return super(EditUserImg, self).get(request, form=form)


# def edit_user_img(request):
#     form = EditUserPhoto()
#     if request.method == 'POST':
#         form = EditUserPhoto(request.POST, request.FILES)
#         if form.is_valid():
#             if 'photo' in request.FILES:
#                 form.photo = request.FILES['photo']
#             form.save(commit=True)
#             return HttpResponseRedirect(reverse('accounts:settings'))
#         else:
#             print(form.errors)
#         context = {
#             'form': form,
#             'page_title': 'Настройки',
#         }
#         return render(request, 'accounts/add_simple_flower.html', context)


class RegisterView(PermissionRequiredMixin, FormView):
    permission_required = 'polls.can_vote'

    form_class = RegisterForm
    page_title = 'Register'
    template_name = 'accounts/register.html'

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context['page'] = 3
        context['page_title'] = 'Создать пользователя'
        return context

    def get(self, request):
        form = RegisterForm()

        return super(RegisterView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            new_profile = User.objects.create_user(
                username=data['username'],
                password=data['password'],
            )
            if new_profile:
                return HttpResponseRedirect(reverse('accounts:settings'))

        return super(RegisterView, self).get(request, form=form)


class LoginView(FormView):
    form_class = LoginForm
    page_title = 'Login'
    template_name = 'accounts/login.html'

    def get(self, request):
        form = LoginForm()
        return super(LoginView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('Chat:chat_choice'))

        return super(LoginView, self).get(request, form=form)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))
