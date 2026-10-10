# Yalnız müəllim üçün — dərsdə YAZILMIR, tələbəyə göstərilmir.
# API-nin hər ünvanını yoxlayır:  uv run manage.py test api     (hamısı: uv run manage.py test)
from rest_framework.test import APITestCase

from blog.models import Post, Category, Tag, Comment


class Lesson15ApiTests(APITestCase):
    fixtures = ["demo_full"]

    # ── [DƏRS 15] PostViewSet + Router ──
    def test_api_root_and_router_urls(self):
        r = self.client.get("/api/")
        self.assertEqual(r.status_code, 200)
        for key in ["posts", "categories", "tags", "comments"]:
            self.assertIn(key, r.json(), key)

    def test_post_crud_via_viewset(self):
        self.assertEqual(len(self.client.get("/api/posts/").json()), 9)
        data = {"title": "ViewSet ilə post", "author": 2, "category": 2, "tags": [4], "content": "Router işlədi."}
        r = self.client.post("/api/posts/", data, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        pk = r.json()["id"]
        self.assertEqual(self.client.get(f"/api/posts/{pk}/").json()["title"], "ViewSet ilə post")
        r = self.client.patch(f"/api/posts/{pk}/", {"title": "Dəyişdi"}, format="json")   # ViewSet PATCH-i də bilir
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Post.objects.get(id=pk).title, "Dəyişdi")
        self.assertEqual(self.client.delete(f"/api/posts/{pk}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/posts/{pk}/").status_code, 404)
        self.assertEqual(self.client.get("/api/posts/999/").status_code, 404)

    def test_post_rich_fields(self):
        p = self.client.get("/api/posts/1/").json()
        self.assertEqual(p["author"], 1)
        self.assertEqual(p["author_name"], "nigar")                 # ReadOnlyField(source=)
        self.assertEqual(p["category_name"], "Proqramlaşdırma")    # [EV 15] bonus
        self.assertEqual(p["like_count"], 0)                       # SerializerMethodField
        self.assertEqual(p["comment_count"], 3)                    # [EV 15] 3 — post 1: şərh 1, 2, 7
        self.assertEqual(len(p["comments"]), 3)                    # nested
        self.assertEqual(p["comments"][0]["author_name"], "nigar") # ordering -created_at → şərh 7
        Post.objects.get(id=1).likes.add(2, 3)
        self.assertEqual(self.client.get("/api/posts/1/").json()["like_count"], 2)

    def test_post_comments_action(self):
        r = self.client.get("/api/posts/1/comments/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 2)                         # parent=None → cavab (7) yoxdur
        self.assertEqual(self.client.get("/api/posts/999/comments/").status_code, 404)

    # ── [PRAKTİKA 15] Category/Tag ViewSet · [DƏRS 15] categories posts action · [EV 15] post_count, tags posts ──
    def test_category_and_tag_viewsets(self):
        cats = self.client.get("/api/categories/").json()
        self.assertEqual(len(cats), 3)
        self.assertEqual(cats[0]["post_count"], 2)                 # [EV 15] 1 — ordering name → "Kitablar" birinci: post 4, 8
        r = self.client.post("/api/categories/", {"name": "İdman", "slug": "idman"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["post_count"], 0)
        self.assertEqual(self.client.get("/api/categories/2/posts/").status_code, 200)
        self.assertEqual(len(self.client.get("/api/categories/2/posts/").json()), 3)   # Oyunlar: 2, 5, 7
        self.assertEqual(len(self.client.get("/api/tags/").json()), 5)
        self.assertNotIn("post_count", self.client.get("/api/tags/1/").json())
        self.assertEqual(len(self.client.get("/api/tags/1/posts/").json()), 4)         # [EV 15] 2 — python: 1, 3, 6, 9
        self.assertEqual(self.client.delete("/api/tags/5/").status_code, 204)
        self.assertEqual(Tag.objects.count(), 4)

    # ── [DƏRS 15] praktikadan sonra ──
    def test_comment_viewset(self):
        self.assertEqual(len(self.client.get("/api/comments/").json()), 6)   # is_active=False olan 4-cü yoxdur
        r = self.client.post("/api/comments/", {"post": 3, "author": 2, "text": "API-dən şərh"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.json()["author_name"], "murad")
        self.assertEqual(Comment.objects.count(), 8)
        self.assertEqual(self.client.delete(f"/api/comments/{r.json()['id']}/").status_code, 204)

    def test_stats_and_html(self):
        self.assertEqual(self.client.get("/api/stats/").json()["post_count"], 9)
        for url in ["/", "/post/1/", "/categories/", "/tag/python/", "/admin/login/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
