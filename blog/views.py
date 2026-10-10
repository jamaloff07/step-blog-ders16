from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from .forms import CommentForm, PostForm, CategoryForm, ContactForm
from .models import Post, Category, Tag, Comment, ContactMessage

# Nişanlar:
#   [DƏRS 13]     — müəllim I hissədə canlı yazır
#   [PRAKTİKA 13] — tələbə II hissədə yazır
#   [EV 13]       — ev tapşırığının həlli
#
# Bu dərsdə YENİ SƏHİFƏ demək olar yoxdur — eyni səhifələr class ilə yenidən yazılır.
# FBV-də hər şeyi özümüz yazırdıq. CBV-də Django-nun hazır class-ından inheritance alırıq (Dərs 4)
# və yalnız FƏRQLİ olan hissəni override edirik.
#
#   ListView   → siyahı səhifəsi          CreateView → yaratma formu
#   DetailView → bir obyektin səhifəsi    UpdateView → redaktə formu      DeleteView → silmə təsdiqi


# ═════════════════════════ POSTLAR ═════════════════════════

# [DƏRS 13] əvvəl: def post_list(request) — 3 sətir. İndi: atributlar + bir metod
class PostListView(ListView):
    model = Post                                                  # hansı modelin siyahısı
    template_name = "blog/post_list.html"                         # hansı template
    context_object_name = "posts"                                 # template-də siyahının adı (default: object_list)
    paginate_by = 4                                               # [DƏRS 13] səhifələmə: hər səhifədə 4 post

    def get_queryset(self):                                       # "hansı postlar?" — default: Post.objects.all()
        posts = Post.objects.filter(is_published=True)

        # [DƏRS 13] praktikadan sonra müəllim — axtarış: /?q=python
        q = self.request.GET.get("q")                             # URL-dəki ?q=... ; yoxdursa None
        if q:
            # [EV 13] bonus — Q ilə "VƏ YA": başlıqda və ya mətndə. Praktikada yalnız title__icontains idi
            posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q))
        return posts

    def get_context_data(self, **kwargs):                         # template-ə ƏLAVƏ dəyişən göndərmək
        context = super().get_context_data(**kwargs)              # əvvəlcə parent-in hazırladığını al (Dərs 4: super)
        context["q"] = self.request.GET.get("q", "")              # [DƏRS 13] praktikadan sonra müəllim — axtarış sözü — başlıqda və qutuda göstərilir
        return context


# post_detail FBV olaraq QALIR — içində şərh formu var (GET + POST + əlavə məntiq).
# Qayda: hazır generic view-a tam oturmayan view-u zorla CBV etmirik.
def post_detail(request, post_id):                                # [DƏRS 9]
    post = get_object_or_404(Post, id=post_id)

    # [REFERANS 12] qaralamanı yalnız öz müəllifi aça bilər, başqaları üçün 404
    if not post.is_published and post.author != request.user:
        raise Http404("Post tapılmadı")

    # [DƏRS 11] şərh formu — eyni view həm göstərir (GET), həm qəbul edir (POST)
    if request.method == "POST":
        if not request.user.is_authenticated:                     # [EV 12] tapşırıq 2 — şərhi yalnız giriş edən yazır
            return redirect("accounts:login")
        form = CommentForm(request.POST)                          # formu gələn məlumatla doldur
        if form.is_valid():                                       # bütün yoxlamalar keçdi?
            comment = form.save(commit=False)                     # obyekt yarat, amma bazaya HƏLƏ yazma
            comment.post = post                                   # formda olmayan sahəni özümüz doldururuq
            comment.author = request.user                         # [EV 12] tapşırıq 2
            comment.save()                                        # indi yaz
            messages.success(request, "Şərhin əlavə olundu.")
            return redirect(post)                                 # POST-dan sonra HƏMİŞƏ redirect
    else:
        form = CommentForm()                                      # GET → boş form

    # [EV 9] tapşırıq 1 — baxış sayı
    post.views += 1
    post.save()

    # [PRAKTİKA 11] parent=None → yalnız əsas şərhlər. Cavablar template-də comment.replies ilə gəlir
    comments = post.comments.filter(is_active=True, parent=None)

    # [REFERANS 10] oxşar postlar (tələbəyə verilmir)
    similar = Post.objects.filter(category=post.category, is_published=True)
    similar = similar.exclude(id=post.id)[:3]

    context = {"post": post, "comments": comments, "similar": similar, "form": form}
    return render(request, "blog/post_detail.html", context)


# [DƏRS 13] əvvəl: def post_create — 12 sətir. Form göstərmək, yoxlamaq, saxlamaq, redirect → CreateView özü edir
class PostCreateView(LoginRequiredMixin, CreateView):             # mixin SOLDA yazılır (Dərs 4: MRO)
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    extra_context = {"page_title": "Yeni post"}                   # template-ə sabit əlavə dəyişən

    def form_valid(self, form):                                   # form düzgündürsə, saxlamazdan ƏVVƏL çağırılır
        form.instance.author = self.request.user                  # müəllif = giriş edən
        messages.success(self.request, "Post yaradıldı.")
        return super().form_valid(form)                           # saxla + get_absolute_url-a redirect


# [DƏRS 13] əvvəl: def post_edit + "if post.author != request.user"
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    pk_url_kwarg = "post_id"                                      # URL-də <int:post_id> yazmışıq (default: pk)
    extra_context = {"page_title": "Postu redaktə et"}

    def test_func(self):                                          # True → burax, False → 403
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.info(self.request, "Post yeniləndi.")
        return super().form_valid(form)


# [DƏRS 13] əvvəl: def post_delete
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("blog:post_list")                  # silinəndən sonra hara (reverse_lazy: class səviyyəsində reverse)

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.warning(self.request, "Post silindi.")
        return super().form_valid(form)


@login_required                                                   # [EV 13] tapşırıq 2 — bəyən / bəyənməkdən imtina
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        if request.user in post.likes.all():                      # artıq bəyənib → geri götür
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return redirect(post)


# ═════════════════════════ SİYAHI SƏHİFƏLƏRİ ═════════════════════════

class AuthorPostListView(ListView):                               # [REFERANS 13] — əvvəl: def author_posts
    template_name = "blog/author_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        name = self.kwargs["name"]                                # URL-dəki <str:name> → self.kwargs
        return Post.objects.filter(author__username=name, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = self.kwargs["name"]
        return context


class MyPostListView(LoginRequiredMixin, ListView):               # [REFERANS 13] — əvvəl: @login_required def my_posts
    template_name = "blog/my_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class LatestPostListView(ListView):                               # [REFERANS 13] — əvvəl: def latest
    template_name = "blog/latest.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(is_published=True)[:3]         # sabit sorğu üçün metod lazım deyil — atribut bəsdir


class LikedPostListView(LoginRequiredMixin, ListView):            # [REFERANS 13] — "Bəyəndiklərim"
    template_name = "blog/liked_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        return self.request.user.liked_posts.filter(is_published=True)   # related_name="liked_posts"


# ═════════════════════════ KATEQORİYALAR VƏ TEQLƏR ═════════════════════════

class CategoryListView(ListView):                                 # [PRAKTİKA 13] — əvvəl: def category_list
    template_name = "blog/category_list.html"
    context_object_name = "categories"
    queryset = Category.objects.annotate(post_count=Count("posts"))


# [DƏRS 13] əvvəl: def category_detail. DetailView obyekti URL-dəki <slug:slug>-a görə özü tapır, tapmasa 404
class CategoryDetailView(DetailView):
    model = Category
    template_name = "blog/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = self.object.posts.filter(is_published=True)    # self.object = tapılan kateqoriya
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):         # [REFERANS 13] — əvvəl: def category_create
    model = Category
    form_class = CategoryForm
    template_name = "blog/category_form.html"
    success_url = reverse_lazy("blog:category_list")              # Category-də get_absolute_url yoxdur → success_url lazımdır


class TagDetailView(DetailView):                                  # [PRAKTİKA 13] — CategoryDetailView-un əkizi
    model = Tag
    template_name = "blog/tag_detail.html"
    context_object_name = "tag"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = self.object.posts.filter(is_published=True)
        return context


class TagListView(ListView):                                      # [REFERANS 13] — əvvəl: def tag_list
    template_name = "blog/tag_list.html"
    context_object_name = "tags"
    queryset = Tag.objects.annotate(post_count=Count("posts"))


# ═════════════════════════ ŞƏRHLƏR (FBV qalır) ═════════════════════════

@login_required                                                   # [EV 12] tapşırıq 2 — cavab da giriş tələb edir
def comment_reply(request, comment_id):                           # [DƏRS 11] praktikadan sonra müəllim
    parent = get_object_or_404(Comment, id=comment_id, is_active=True)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = parent.post                              # cavab da eyni posta aiddir
            reply.parent = parent                                 # kimə cavab verilir
            reply.author = request.user                           # [EV 12] tapşırıq 2
            reply.save()
            messages.success(request, "Cavabın əlavə olundu.")
            return redirect(parent.post)
    else:
        form = CommentForm()
    context = {"form": form, "parent": parent}
    return render(request, "blog/comment_reply.html", context)


@login_required                                                   # [REFERANS 12] öz şərhini silmək
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        raise PermissionDenied
    if request.method == "POST":                                  # silmək yalnız POST ilə
        comment.delete()
        messages.warning(request, "Şərh silindi.")
    return redirect(comment.post)


# ═════════════════════════ DİGƏR SƏHİFƏLƏR ═════════════════════════

class AboutView(TemplateView):                                    # [REFERANS 13] — əvvəl: def about
    template_name = "blog/about.html"                             # məlumatsız səhifə üçün ən sadə CBV


def contact(request):                                             # [REFERANS 11]
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data                              # yoxlanmış məlumat — adi dict
            ContactMessage.objects.create(name=data["name"], email=data["email"], message=data["message"])
            messages.success(request, "Mesajın göndərildi. Təşəkkürlər!")
            return redirect("blog:contact")
    else:
        form = ContactForm()
    return render(request, "blog/contact.html", {"form": form})


def stats(request):                                               # [EV 9] bonus
    published = Post.objects.filter(is_published=True)

    # [REFERANS 10] ən çox şərh yazılan post: əvvəl say, sonra sırala
    most_commented = published.annotate(comment_count=Count("comments"))
    most_commented = most_commented.order_by("-comment_count").first()

    context = {
        "post_count": published.count(),
        "category_count": Category.objects.count(),
        "top_post": published.order_by("-views").first(),
        "comment_count": Comment.objects.count(),                 # [REFERANS 10]
        "tag_count": Tag.objects.count(),                         # [REFERANS 10]
        "most_commented": most_commented,                         # [REFERANS 10]
    }
    return render(request, "blog/stats.html", context)
