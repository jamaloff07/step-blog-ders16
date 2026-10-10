# Yalnız müəllim üçün — dərsdə YAZILMIR, tələbəyə göstərilmir.
# Layihənin hər URL-ni yoxlayır:  python manage.py test
# Fixture istifadəçiləri: nigar, murad, aysel, kamran — parol hamısında step12345
from django.contrib.auth.models import User
from django.test import TestCase

from .models import Post, Comment


class Lesson13Tests(TestCase):
    fixtures = ["demo_full"]

    def login(self, name):
        self.assertTrue(self.client.login(username=name, password="step12345"))

    def test_public_pages(self):
        urls = ["/", "/post/1/", "/about/", "/contact/", "/categories/", "/category/oyunlar/", "/author/nigar/",
                "/stats/", "/latest/", "/tag/python/", "/tags/", "/?q=git", "/?page=2",
                "/accounts/login/", "/accounts/register/"]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertContains(self.client.get("/author/nigar/"), "Git nədir")

    def test_login_required_redirects(self):
        for url in ["/post/new/", "/post/1/edit/", "/post/1/delete/", "/my-posts/", "/comment/1/reply/", "/liked/", "/category/new/",
                    "/accounts/profile/", "/accounts/password/"]:
            r = self.client.get(url)
            self.assertRedirects(r, f"/accounts/login/?next={url}", msg_prefix=url)

    def test_register_login_logout(self):
        data = {"username": "yeni", "email": "yeni@step.az", "password1": "Cetin-Parol-99", "password2": "Cetin-Parol-99"}
        r = self.client.post("/accounts/register/", data, follow=True)
        self.assertContains(r, "Xoş gəldin, yeni")
        self.assertContains(r, "@yeni")                            # avtomatik giriş + navbar
        self.assertNotEqual(User.objects.get(username="yeni").password, "Cetin-Parol-99")   # hash
        r = self.client.post("/accounts/logout/", follow=True)
        self.assertContains(r, "Qeydiyyat")
        self.assertEqual(self.client.get("/accounts/logout/").status_code, 405)              # GET olmaz
        r = self.client.post("/accounts/login/?next=/my-posts/", {"username": "yeni", "password": "Cetin-Parol-99"})
        self.assertRedirects(r, "/my-posts/")

    def test_create_sets_author(self):
        self.login("aysel")
        data = {"title": "Yeni kitab icmalı", "category": 3, "tags": [5], "content": "Mətn.", "is_published": "on"}
        r = self.client.post("/post/new/", data, follow=True)
        post = Post.objects.get(title="Yeni kitab icmalı")
        self.assertEqual(post.author.username, "aysel")
        self.assertEqual(post.tags.count(), 1)                     # save_m2m
        self.assertNotContains(self.client.get("/post/new/"), "Müəllif")

    def test_ownership(self):
        self.login("murad")                                       # post 1 nigar-ındır
        self.assertEqual(self.client.get("/post/1/edit/").status_code, 403)
        self.assertEqual(self.client.post("/post/1/delete/").status_code, 403)
        self.assertContains(self.client.get("/post/1/edit/"), "İcazə yoxdur", status_code=403)
        self.assertNotContains(self.client.get("/post/1/"), "Redaktə et")
        self.assertContains(self.client.get("/post/2/"), "Redaktə et")        # post 2 murad-ındır
        self.assertEqual(self.client.get("/post/2/edit/").status_code, 200)
        self.assertEqual(Post.objects.count(), 9)

    def test_my_posts_and_drafts(self):
        self.login("murad")
        Post.objects.filter(id=5).update(is_published=False)
        r = self.client.get("/my-posts/")
        self.assertContains(r, "Minecraft")
        self.assertContains(r, "FIFA")
        self.assertContains(r, "qaralama")
        self.assertNotContains(r, "Git nədir")
        self.assertNotContains(self.client.get("/"), "FIFA")

    def test_comments_need_login(self):
        r = self.client.post("/post/3/", {"text": "Anonim şərh yazıram"})
        self.assertRedirects(r, "/accounts/login/")
        self.assertContains(self.client.get("/post/3/"), "daxil ol")
        self.login("aysel")
        self.client.post("/post/3/", {"text": "Çox maraqlıdır!"})
        c = Comment.objects.get(text="Çox maraqlıdır!")
        self.assertEqual(c.author.username, "aysel")
        self.client.post("/comment/%d/reply/" % c.id, {"text": "Öz-özümə cavab"})
        self.assertEqual(Comment.objects.get(text="Öz-özümə cavab").author.username, "aysel")
        Comment.objects.create(post_id=4, text="Köhnə, müəllifsiz şərh")
        self.assertContains(self.client.get("/post/4/"), "qonaq")             # müəllifsiz köhnə şərh

    def test_comment_delete(self):
        self.login("murad")                                       # şərh 1 kamran-ındır
        self.assertEqual(self.client.post("/comment/1/delete/").status_code, 403)
        self.client.logout(); self.login("kamran")
        r = self.client.post("/comment/1/delete/", follow=True)
        self.assertContains(r, "Şərh silindi")
        self.assertFalse(Comment.objects.filter(id=1).exists())

    def test_profile_password(self):
        self.login("nigar")
        r = self.client.get("/accounts/profile/")
        self.assertContains(r, "nigar@step.az")
        data = {"old_password": "step12345", "new_password1": "Yeni-Parol-2026", "new_password2": "Yeni-Parol-2026"}
        self.assertRedirects(self.client.post("/accounts/password/", data), "/accounts/profile/")

    def test_cbv_edit_delete_flow(self):
        self.login("murad")
        data = {"title": "FIFA taktikası 2", "category": 2, "content": "Yeni mətn.", "is_published": "on"}
        r = self.client.post("/post/5/edit/", data, follow=True)
        self.assertRedirects(r, "/post/5/")
        self.assertContains(r, "Post yeniləndi")
        r = self.client.post("/post/5/delete/", follow=True)
        self.assertRedirects(r, "/")
        self.assertContains(r, "Post silindi")
        self.assertEqual(Post.objects.count(), 8)

    def test_pagination(self):
        r = self.client.get("/")
        self.assertEqual(len(r.context["posts"]), 4)
        self.assertContains(r, "1 / 3")
        self.assertContains(r, "?page=2")
        self.assertEqual(len(self.client.get("/?page=3").context["posts"]), 1)
        self.assertEqual(self.client.get("/?page=9").status_code, 404)

    def test_search(self):
        r = self.client.get("/?q=django")
        self.assertContains(r, "Django-da ilk view")
        self.assertNotContains(r, "FIFA")
        self.assertContains(r, "1 nəticə")
        r = self.client.get("/?q=elektrik")                       # yalnız mətndə var → Q
        self.assertContains(r, "Minecraft")
        r = self.client.get("/?q=a")                              # çox nəticə → səhifələmə q-nu saxlayır
        self.assertContains(r, "?page=2&q=a")

    def test_like(self):
        self.assertRedirects(self.client.post("/post/1/like/"), "/accounts/login/?next=/post/1/like/")
        self.login("aysel")
        self.client.post("/post/1/like/")
        self.assertEqual(Post.objects.get(id=1).likes.count(), 1)
        self.assertContains(self.client.get("/post/1/"), "Bəyənmişəm")
        self.assertContains(self.client.get("/liked/"), "Python-da ilk addım")
        self.client.post("/post/1/like/")
        self.assertEqual(Post.objects.get(id=1).likes.count(), 0)

    def test_custom_404(self):
        r = self.client.get("/post/999/")
        self.assertContains(r, "Səhifə tapılmadı", status_code=404)
        self.assertEqual(self.client.get("/category/futbol/").status_code, 404)
        self.assertEqual(self.client.get("/tag/yox/").status_code, 404)

    def test_admin(self):
        # "admin" superuser artıq demo_full.json-dadır (parol step12345)
        self.login("admin")
        for url in ["/admin/blog/post/1/change/", "/admin/blog/comment/", "/admin/auth/user/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
