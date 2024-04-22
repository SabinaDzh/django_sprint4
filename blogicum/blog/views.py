from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    ListView,
    UpdateView,
    DetailView,
    CreateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.db.models import Count
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Category, User, Comment
from .forms import PostForm, CommentForm, UpdateProfileForm


PAGINATE_COUNT = 10


def get_general_posts_filter():
    return (
        Post.objects.select_related("author", "location", "category")
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )


class IndexListView(ListView):
    paginate_by = PAGINATE_COUNT
    template_name = "blog/index.html"
    context_object_name = "posts"
    model = Post

    def get_queryset(self):
        queryset = (
            Post.objects.filter(
                pub_date__lt=timezone.now(),
                is_published=True,
                category__is_published=True,
            ).annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )
        return queryset


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "blog/user.html"
    form_class = UpdateProfileForm
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class ProfileListView(ListView):
    model = User
    template_name = "blog/profile.html"
    paginate_by = PAGINATE_COUNT

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs["username"])
        return (
            Post.objects.select_related(
                "author",
                "location",
                "category",
            )
            .filter(author=self.author)
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"
    paginate_by = PAGINATE_COUNT

    def get_queryset(self):
        return super().get_queryset(
        ).select_related("author", "location", "category",)

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        if not post.is_published and post.author != self.request.user:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context


class CategoryListView(ListView):
    model = Post
    template_name = "blog/category.html"
    paginate_by = PAGINATE_COUNT

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        self.category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return self.category.posts.filter(
            pub_date__lt=timezone.now(),
            is_published=True
        ).annotate(comment_count=Count("comments")
                   ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs["category_slug"],
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:profile")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy("blog:profile", kwargs={"username": username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        if post.is_published and post.author == self.request.user:
            return post
        else:
            raise Http404

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Post,
            pk=kwargs.get("post_id"),
        )
        if instance.author != request.user:
            return redirect("blog:post_detail", self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.object.pk}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        if post.is_published and post.author == self.request.user:
            return post
        else:
            raise Http404

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Post,
            pk=kwargs.get("post_id")
        )
        if instance.author != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_comment = post
        comment.save()
    return redirect("blog:post_detail", post_id=post_id)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs.get("comment_id"))
        if request.user != instance.author:
            return redirect("blog:post_detail", self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"
    success_url = reverse_lazy("blog:post_detail")

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get("comment_id"))
        if self.request.user != comment.author:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )
