from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Category, Comment
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.paginator import Paginator
from . import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Q


User = get_user_model()


def filter_posts(objects):
    current_time = timezone.now()
    return objects.filter(
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True
    )


class AuthorRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != self.request.user:
            return redirect('blog:post_detail', self.object.id)
        return super(AuthorRequiredMixin, self).dispatch(
            request,
            *args,
            **kwargs
        )


def index(request):
    template = "blog/index.html"
    posts = Post.objects.select_related("category", "author", "location")
    post_list = filter_posts(posts)
    for post in post_list:
        post.comment_count = Comment.objects.filter(post=post).count()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'post_list': post_list,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# class IndexListView(ListView):
#     template_name = "blog/index.html"
#     model = Post
#     posts = Post.objects.select_related("category", "author", "location")
#     post_list = filter_posts(posts)
#     queryset = post_list
#     for post in queryset:
#         post.comment_count = Comment.objects.filter(post=post).count()
#     paginate_by = 10


def post_detail(request, pk):
    template = "blog/detail.html"
    current_time = timezone.now()
    current_user = None
    if request.user.is_authenticated:
        current_user = request.user
    posts = Post.objects.select_related("category", "author", "location")
    post = get_object_or_404(
        posts,
        Q(pub_date__lte=current_time) | Q(author=current_user),
        Q(is_published=True) | Q(author=current_user),
        Q(category__is_published=True) | Q(author=current_user),
        pk=pk,
    )
    context = {
        "post": post,
        'form': forms.CommentForm(),
        'comments': post.comments.select_related('author'),
    }
    return render(request, template, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = forms.PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = forms.PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.id}
        )


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:index',
        )


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = forms.CommentForm(request.POST)
    if form.is_valid():
        # Создаём объект комментария, но не сохраняем его в БД.
        comment = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        comment.author = request.user
        # В поле birthday передаём объект дня рождения.
        comment.post = post
        post.comment_count += 1
        # Сохраняем объект в БД.
        comment.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('blog:post_detail', pk=pk)


class CommentUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Comment
    fields = ('text', )
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        context = self.get_context_data()
        comment = context['comment']
        post = comment.post
        post.comment_count -= 1
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


def category_posts(request, category_slug):
    template = "blog/category.html"
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    posts = category.posts.select_related("category", "author", "location")
    post_list = filter_posts(posts)

    for post in post_list:
        post.comment_count = Comment.objects.filter(post=post).count()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "post_list": post_list,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):

    template_name = 'blog/profile.html'

    profile = get_object_or_404(User, username=username)

    posts = Post.objects.filter(author=profile.id)
    for post in posts:
        post.comment_count = Comment.objects.filter(post=post).count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'page_obj': page_obj
    }

    return render(request, template_name, context)


class UpdateUser(LoginRequiredMixin, UpdateView):
    model = User
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    template_name = 'blog/user.html'

    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.username}
        )
    # def get_absolute_url(self):
    #     context = self.get_context_data()
    #     user = context['user']
    #     return reverse(
    #         'service:profile',
    #         kwargs={'username': user.username}
    #     )
    # success_url = reverse_lazy('service:index')
