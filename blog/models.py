from django.contrib.auth.models import User  # [DƏRS 12] Django-nun hazır istifadəçi modeli
from django.db import models
from django.urls import reverse

# Model = cədvəl, obyekt = sətir, sahə = sütun.
# Model dəyişəndən sonra HƏMİŞƏ:  makemigrations  →  migrate
#
# Nişanlar:  [DƏRS 13] müəllim · [DƏRS 13] praktikadan sonra müəllim · [PRAKTİKA 13] tələbə · [EV 13] tapşırıq 1–3 / bonus · [REFERANS 13] tələbəyə verilmir
# Köhnə nişanlar ([DƏRS 12] …) həmin sətrin hansı dərsdə yarandığını göstərir.


# [PRAKTİKA 9] tələbə yazıb.
# [DƏRS 10] Category sinfi Post-un ÜSTÜNƏ köçürüldü — Post ona istinad edir, ona görə əvvəl tanınmalıdır.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)                          # URL-də işlənir, təkrarlana bilməz
    description = models.TextField(blank=True)                    # blank=True → formda boş qala bilər

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"                        # admində "Categorys" yazılmasın

    def __str__(self):
        return self.name


# [PRAKTİKA 10] tələbə yazır — Category-nin əkizi
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# [DƏRS 9] müəllim yazıb
class Post(models.Model):
    title = models.CharField(max_length=200)                      # qısa mətn — max_length = maksimum simvol sayı

    # [DƏRS 12] CharField idi → ForeignKey(User) oldu. Post real istifadəçiyə bağlanır.
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,                                 # istifadəçi silinsə, postları da silinir
        related_name="posts",                                     # user.posts.all()
    )

    # [DƏRS 10] CharField idi → ForeignKey oldu. Post kateqoriyanın ÖZÜNƏ bağlanır, mətnə yox.
    category = models.ForeignKey(
        Category,                                                 # hansı modelə bağlanır
        on_delete=models.PROTECT,                                 # postu olan kateqoriyanı silmək olmaz
        related_name="posts",                                     # tərs əlaqənin adı: category.posts.all()
    )

    content = models.TextField()                                  # uzun mətn — limitsiz
    is_published = models.BooleanField(default=True)              # dərc olunubmu?
    views = models.PositiveIntegerField(default=0)                # baxış sayı, mənfi ola bilməz
    created_at = models.DateTimeField(auto_now_add=True)          # yaranma vaxtı avtomatik yazılır

    # [EV 9] tapşırıq 2
    is_featured = models.BooleanField(default=False)

    # [DƏRS 10] şəkil — fayl media/posts/ qovluğuna düşür, bazada yalnız yolu saxlanır
    image = models.ImageField(upload_to="posts/", blank=True)

    # [PRAKTİKA 10] bir postun çox teqi, bir teqin çox postu ola bilər
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")

    # [EV 13] tapşırıq 1 — bəyənmə: bir postu çox user bəyənir, bir user çox postu bəyənir → M2M
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    class Meta:
        ordering = ["-created_at"]                                # default sıra: ən yenisi birinci

    def __str__(self):                                            # admin və shell-də belə görünür
        return self.title

    # [DƏRS 11] bu postun öz ünvanı. redirect(post) və admin-dəki "Saytda bax" bunu işlədir
    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.id])


# [DƏRS 10] müəllim yazır — bir postun çox şərhi olur
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,                                 # post silinsə, şərhləri də silinir
        related_name="comments",                                  # post.comments.all()
    )

    # [EV 12] tapşırıq 1 — "name" sahəsi silindi, yerinə real istifadəçi gəldi.
    # null=True → köhnə şərhlərin müəllifi boş qalır (template-də "qonaq" yazılır)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # [EV 10] tapşırıq 1 — admin şərhi gizlədə bilsin
    is_active = models.BooleanField(default=True)

    # [PRAKTİKA 11] cavab = başqa şərhə bağlanan şərh. "self" → model özünə istinad edir.
    # Adi şərhdə parent boşdur (None), cavabda — cavab verilən şərhdir.
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,                                 # şərh silinsə, cavabları da silinir
        null=True,                                                # bazada boş qala bilər
        blank=True,                                               # formda boş qala bilər
        related_name="replies",                                   # comment.replies.all()
    )

    class Meta:
        ordering = ["-created_at"]                                # [EV 10] tapşırıq 1 — ən yeni şərh birinci

    def __str__(self):
        return f"{self.author}: {self.text[:30]}"


# [REFERANS 11] — əlaqə formundan gələn mesajlar bazada saxlanır, admin oxuyur
class ContactMessage(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"
