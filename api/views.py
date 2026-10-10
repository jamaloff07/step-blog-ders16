from django.contrib import auth
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from .permissions import IsOwnerOrReadOnly
from blog.models import Post, Category, Tag, Comment
from .serializers import *

# Dərs 14-də hər model üçün 2 funksiya × ~20 sətir yazırdıq (list + detail, içində if request.method ...).
# Dərs 13-dəki fikir (CBV): hazır class-dan inheritance al, yalnız fərqli olanı yaz.
#
#   ModelViewSet = list + create + retrieve + update + partial_update + destroy — hamısı bir class-da.
#   Bizim yazdığımız: queryset (hansı obyektlər?) + serializer_class (hansı tərcüməçi?). Vəssalam.
#   URL-ləri də özümüz yazmırıq — urls.py-dakı Router ViewSet-dən 2 ünvanı özü düzəldir.
#
#   @action — ViewSet-ə ƏLAVƏ ünvan: /api/posts/3/comments/   (detail=True → bir obyekt üçün)
#
# Nişanlar:  [DƏRS 15] müəllim · [DƏRS 15] praktikadan sonra müəllim · [PRAKTİKA 15] tələbə · [EV 15] tapşırıq 1–3 / bonus · [REFERANS 15] tələbəyə verilmir


# [DƏRS 15] əvvəl: post_list + post_detail — 2 funksiya, 35 sətir. İndi: 1 class, 2 sətir (+ action)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(
        is_published=True
    )  # "hansı obyektlər?" — yalnız dərc olunmuşlar (Dərs 13: get_queryset)
    serializer_class = PostSerializer  # "hansı serializer?"
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]  # yalnız giriş etmiş istifadəçi post yarada bilər, hamı oxuya bilər

    # if form.is_valid():
    # author=self.request.user
    # form.save()
    def perform_create(
        self, serializer
    ):  # post yaratmaq üçün override: müəllif = giriş etmiş istifadəçi
        serializer.save(
            author=self.request.user
        )  # self.request.user = giriş etmiş istifadəçi (Dərs 13: get_serializer)

    # [DƏRS 15] əlavə ünvan: GET /api/posts/3/comments/ — yalnız bu postun əsas şərhləri
    @action(
        detail=True, methods=["get"]
    )  # detail=True → URL-də pk var; metodun adı = ünvanın son hissəsi
    def comments(self, request, pk=None):
        post = self.get_object()  # pk-ya görə tapır, tapmasa 404 (DetailView-dakı kimi)
        comments = post.comments.filter(is_active=True, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


# [PRAKTİKA 15] — əvvəl: category_list + category_detail. PostViewSet-in əkizi (tələbə yazır)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # [DƏRS 15] praktikadan SONRA müəllim yazır — GET /api/categories/2/posts/ (PostViewSet.comments-in əkizi)
    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        category = self.get_object()
        posts = category.posts.filter(is_published=True)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


# [PRAKTİKA 15] — əvvəl: tag_list + tag_detail (tələbə yazır)
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # [EV 15] tapşırıq 2 — GET /api/tags/1/posts/ (CategoryViewSet.posts-un əkizi)
    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        tag = self.get_object()
        posts = tag.posts.filter(is_published=True)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


# [DƏRS 15] praktikadan SONRA müəllim yazır — şərhlər üçün tam CRUD (2 sətir!)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_active=True)
    serializer_class = CommentSerializer


# [EV 14] — modelə bağlı deyil, ona görə ViewSet yox, adi @api_view qalır
@api_view(["GET"])
def stats(request):
    data = {
        "post_count": Post.objects.filter(is_published=True).count(),
        "category_count": Category.objects.count(),
        "tag_count": Tag.objects.count(),
    }
    return Response(data)


@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully."}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user

    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "post_count": user.posts.count(),
        "comment_count": user.comments.count(),
    }

    return Response(data)
