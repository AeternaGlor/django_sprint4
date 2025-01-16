from django.shortcuts import get_object_or_404, render
from .models import Post, Category
from django.utils import timezone


def filter_posts(objects):
    current_time = timezone.now()
    return objects.filter(
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True
    )


def index(request):
    template = "blog/index.html"
    posts = Post.objects.select_related("category", "author", "location")
    post_list = filter_posts(posts)[:5]
    context = {"post_list": post_list}
    return render(request, template, context)


def post_detail(request, post_id):
    template = "blog/detail.html"
    current_time = timezone.now()
    posts = Post.objects.select_related("category", "author", "location")
    post = get_object_or_404(
        posts,
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True,
        pk=post_id,
    )
    context = {
        "post": post,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = "blog/category.html"
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    posts = category.posts.select_related("category", "author", "location")
    post_list = filter_posts(posts)
    context = {"category": category, "post_list": post_list}
    return render(request, template, context)
