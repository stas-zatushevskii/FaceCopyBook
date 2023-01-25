from django.shortcuts import render, redirect
from .models import Post, Like
from profiles.models import Profile
from .forms import PostModelFrorm, CommentModelFrorm
from django.views.generic import DeleteView, UpdateView, ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# для классов:
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()

@login_required
def post_comment_create_list_view(request):
    posts = Post.objects.all()
    profile = Profile.objects.get(user=request.user)

    # initial
    p_form = PostModelFrorm()
    c_form = CommentModelFrorm()
    added = False

    # post form
    if 'submit_p_form' in request.POST:
        p_form = PostModelFrorm(request.POST, request.FILES)
        if request.method == 'POST':
            if p_form.is_valid():
                post = p_form.save(commit=False)
                post.author = profile
                post.save()
                p_form = PostModelFrorm()
                added = True

    # comment form
    if 'submit_c_form' in request.POST:
        c_form = CommentModelFrorm(request.POST)
        if request.method == 'POST':
            if c_form.is_valid():
                comment = c_form.save(commit=False)
                comment.author = profile
                # получаям id из формы в которую мы заранее его передали
                comment.post = Post.objects.get(id=request.POST.get('post_id'))
                comment.save()
                c_form = CommentModelFrorm()

    context = {
        'posts': posts,
        'profile': profile,
        'p_form': p_form,
        'c_form': c_form,
        'added': added,
    }

    return render(request, 'posts/main.html', context)


@login_required
def like_dislike_post(request):
    user = request.user

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=user)

        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
        else:
            like, created = Like.objects.get_or_create(author=profile, post_id=post_id, value='Like')
            if not created:
                like.delete()

    return redirect('posts:main-post-view')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/confirm-del.html'
    success_url = '/posts/'

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)
        if not post.author.user == self.request.user:
            messages.warning(self.request, 'Вы не являетесь автором поста')
        return post


class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostModelFrorm
    template_name = 'posts/update.html'
    success_url = '/posts/'
    model = Post

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, 'Вы не являетесь автором поста')
            return super().form_invalid(form)


class PostListByName(ListView):
    model = Post
    template_name = 'posts/founded.html'
    context_object_name = 'posts'

    def get_queryset(self):
        name = str(self.request.GET.get('name')).lower()
        if User.objects.filter(
            Q(username__iregex=name) | Q(username__iregex=name)).exists():
            user = User.objects.get(
                Q(username__iregex=name) | Q(username__iregex=name))
            author = Profile.objects.get(user=user)
            object_list = Post.objects.filter(author=author)
            return object_list
