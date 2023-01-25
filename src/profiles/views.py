from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# для классов :
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def my_profile_view(request):
    obj = Profile.objects.get(user=request.user)
    template = 'profiles/my_profile.html'
    is_edit = False
    form = ProfileForm(
        request.POST or None,
        files=request.FILES or None,
        instance=obj
    )
    if form.is_valid():
        form.save()
        is_edit = True

    context = {
        'obj': obj,
        'is_edit': is_edit,
        'form': form
    }
    return render(request, template, context)


@login_required
def invites_received(request):
    obj = Profile.objects.get(user=request.user)
    invites = Relationship.objects.invitation_received(obj)

    # получаем sender из invites с помощью функции map()
    # map () позволяет применить заданную функцию к каждому
    # элементу в итерируемом объекте
    results = list(map(lambda x: x.sender, invites))
    is_empty = False

    if len(results) == 0:
        is_empty = True

    context = {
        'qs': results,
        'invites': invites,
        'is_empty': is_empty,
    }

    return render(request, 'profiles/my_invites.html', context)


@login_required
def accept_invites(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        recipient = Profile.objects.get(user=request.user)
        relationship = get_object_or_404(Relationship, sender=sender, recipient=recipient)
        if relationship.status == 'send':
            relationship.status = 'accepted'
            relationship.save()
        sender.friends.add(recipient.user)
        recipient.friends.add(sender.user)
    return redirect('profiles:my_invites')


@login_required
def reject_invites(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        recipient = Profile.objects.get(user=request.user)
        relationship = get_object_or_404(Relationship, sender=sender, recipient=recipient)
        relationship.delete()
    return redirect('profiles:my-invites')


@login_required
def profiles_list_view(request):
    user = request.user
    profiles = Profile.objects.get_profiles(user)

    context = {
        'profiles': profiles
    }

    return render(request, 'profiles/profile_list.html', context)


@login_required
def invite_profiles_list_view(request):
    user = request.user
    profiles = Profile.objects.get_all_profiles_to_invite(user)
    user = User.objects.get(username__iexact=request.user)
    profile = Profile.objects.get(user=user)
    recipient = Relationship.objects.filter(sender=profile)
    sender = Relationship.objects.filter(recipient=profile)
    is_empty = False if len(profiles) > 0 else True

    arr_recipient = []
    arr_sender = []

    for obj in recipient:
        arr_recipient.append(obj.recipient.user)

    for obj in sender:
        arr_sender.append(obj.sender.user)

    context = {
        'profiles': profiles,
        'arr_recipient': arr_recipient,
        'arr_sender': arr_sender,
        'is_empty': is_empty
    }

    return render(request, 'profiles/to_invite_list.html', context)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'

    # по сути все это может работать под капотом DetailView
    def get_object(self, slug=None):
        slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=slug)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        recipient = Relationship.objects.filter(sender=profile)
        sender = Relationship.objects.filter(recipient=profile)
        arr_recipient = []
        arr_sender = []

        for obj in recipient:
            arr_recipient.append(obj.recipient.user)

        for obj in sender:
            arr_sender.append(obj.sender.user)
        context['arr_recipient'] = arr_recipient
        context['arr_sender'] = arr_sender
        context['is_empty'] = False
        context['posts'] = self.get_object().get_posts()
        context['num_posts'] = True if self.get_object().get_posts_num() > 0 else False

        return context


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'

    def get_queryset(self):
        queryset = Profile.objects.get_profiles(self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        recipient = Relationship.objects.filter(sender=profile)
        sender = Relationship.objects.filter(recipient=profile)
        arr_recipient = []
        arr_sender = []

        for obj in recipient:
            arr_recipient.append(obj.recipient.user)

        for obj in sender:
            arr_sender.append(obj.sender.user)
        context['arr_recipient'] = arr_recipient
        context['arr_sender'] = arr_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context


@login_required
def send_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(user=request.user)
        recipient = Profile.objects.get(pk=pk)

        relationship = Relationship.objects.create(sender=sender, recipient=recipient, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my_profile')


@login_required
def delete_friend(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(user=request.user)
        recipient = Profile.objects.get(pk=pk)

        # получаем отношение которое было созданно пользователем,
        # или которое было полученно пользователем
        relationship = Relationship.objects.get(
            (Q(sender=sender) & Q(recipient=recipient)) | (Q(sender=recipient) & Q(recipient=sender))
        )
        relationship.delete()

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my_profile')
