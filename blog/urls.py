from django.urls import path

from . import views

app_name = "blog"

# [DƏRS 13] CBV class-dır, path() isə funksiya istəyir → .as_view() class-dan view funksiyası düzəldir.
# URL-lər və name-lər DƏYİŞMƏDİ — ona görə template-lərdəki {% url %} linklərinə toxunmuruq.
urlpatterns = [
    # postlar
    path("", views.PostListView.as_view(), name="post_list"),                                   # [DƏRS 13]
    path("post/new/", views.PostCreateView.as_view(), name="post_create"),                      # [DƏRS 13]
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),                         # FBV qalır
    path("post/<int:post_id>/edit/", views.PostUpdateView.as_view(), name="post_edit"),         # [DƏRS 13]
    path("post/<int:post_id>/delete/", views.PostDeleteView.as_view(), name="post_delete"),     # [DƏRS 13]
    path("post/<int:post_id>/like/", views.post_like, name="post_like"),                        # [EV 13] tapşırıq 2
    # siyahılar
    path("author/<str:name>/", views.AuthorPostListView.as_view(), name="author_posts"),        # [REFERANS 13]
    path("my-posts/", views.MyPostListView.as_view(), name="my_posts"),                         # [REFERANS 13]
    path("latest/", views.LatestPostListView.as_view(), name="latest"),                         # [REFERANS 13]
    path("liked/", views.LikedPostListView.as_view(), name="liked_posts"),                      # [REFERANS 13]
    # kateqoriyalar və teqlər
    path("categories/", views.CategoryListView.as_view(), name="category_list"),                # [PRAKTİKA 13]
    path("category/new/", views.CategoryCreateView.as_view(), name="category_create"),          # [REFERANS 13]
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),  # [DƏRS 13]
    path("tags/", views.TagListView.as_view(), name="tag_list"),                                # [REFERANS 13]
    path("tag/<slug:slug>/", views.TagDetailView.as_view(), name="tag_detail"),                 # [PRAKTİKA 13]

    # şərhlər — FBV
    path("comment/<int:comment_id>/reply/", views.comment_reply, name="comment_reply"),
    path("comment/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),

    # digər
    path("about/", views.AboutView.as_view(), name="about"),                                    # [REFERANS 13]
    path("contact/", views.contact, name="contact"),
    path("stats/", views.stats, name="stats"),
]
