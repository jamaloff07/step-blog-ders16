from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from . import views

app_name = "api"

# [DƏRS 15] Router: ViewSet-i qeydiyyatdan keçir → ünvanları özü düzəldir.
#   router.register("posts", PostViewSet)  →  /api/posts/            (list, create)
#                                             /api/posts/<pk>/       (retrieve, update, partial_update, destroy)
#                                             /api/posts/<pk>/comments/   (@action)
# Dərs 14-dəki 2 path() sətri və .as_view() — artıq lazım deyil.
# /api/ ünvanının özü də işləyir — DefaultRouter "API root" səhifəsi düzəldir (bütün ünvanların siyahısı).
router = DefaultRouter()
router.register("posts", views.PostViewSet)  # [DƏRS 15]
router.register("categories", views.CategoryViewSet)  # [PRAKTİKA 15]
router.register("tags", views.TagViewSet)  # [PRAKTİKA 15]
router.register("comments", views.CommentViewSet)  # [DƏRS 15] praktikadan sonra

urlpatterns = [
    path("stats/", views.stats, name="stats"),  # [EV 14] — ViewSet deyil, əl ilə
    path("token/", TokenObtainPairView.as_view()),  # POST username+parol → access + refresh
    path("token/refresh/", TokenRefreshView.as_view()),
    path("register/", views.register, name="register"),  # [EV 15] tapşırıq 4 — ViewSet deyil, əl ilə
    path("me/", views.me, name="me"),  # [EV 15] tapşırıq 5 — ViewSet deyil, class-based view
    path("", include(router.urls)),  # router-in düzəltdiyi bütün ünvanlar
]
