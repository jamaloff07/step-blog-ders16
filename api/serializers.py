from rest_framework import serializers
from django.contrib.auth.models import User 
from blog.models import Post, Category, Tag, Comment

# Serializer = model obyekti ⇄ JSON tərcüməçisi (Dərs 14).
# Bu dərsdə JSON-u ZƏNGİNLƏŞDİRİRİK: id yerinə ad, hesablanan sahə, iç-içə (nested) obyektlər.
#
#   ReadOnlyField(source="author.username")  — əlaqəli obyektin BİR sahəsi (yalnız oxunur)
#   SerializerMethodField()                   — get_<ad>() metodunun qaytardığı dəyər (yalnız oxunur)
#   CommentSerializer(many=True, read_only=True) — nested: postun içində şərhlərin siyahısı
#
# Nişanlar:  [DƏRS 15] müəllim · [DƏRS 15] praktikadan sonra müəllim · [PRAKTİKA 15] tələbə · [EV 15] tapşırıq 1–3 / bonus · [REFERANS 15] tələbəyə verilmir


# [DƏRS 15] şərh — ayrıca da işlənir, Post-un içində nested də. Ona görə PostSerializer-dən ƏVVƏL yazılır
class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source="author.username")   # author id-dir; yanında adını da göstəririk

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "author_name", "text", "parent", "created_at"]
        read_only_fields = ["created_at"]


# [DƏRS 14] müəllim yazıb · [DƏRS 15] zənginləşdirildi
class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")   # [DƏRS 15] source: "author" obyektinin "username"-i
    category_name = serializers.ReadOnlyField(source="category.name")   # [EV 15] bonus — author_name-in əkizi
    like_count = serializers.SerializerMethodField()                    # [DƏRS 15] dəyəri aşağıdakı get_like_count verir
    comment_count = serializers.SerializerMethodField()                 # [EV 15] tapşırıq 3 — like_count-un əkizi
    comments = CommentSerializer(many=True, read_only=True)             # [DƏRS 15] nested: related_name="comments"

    class Meta:
        model = Post
        fields = [
            "id", "title", "author", "category", "category_name", "tags",
            "content", "image", "is_published", "views", "created_at",
            "like_count", "comment_count", "comments",
        ]
        read_only_fields = ["views", "created_at"]

    def get_like_count(self, post):                               # ad qaydası: get_ + sahənin adı. post = serializasiya olunan obyekt
        return post.likes.count()

    def get_comment_count(self, post):                            # [EV 15] tapşırıq 3
        return post.comments.filter(is_active=True).count()


# [PRAKTİKA 14] tələbə yazıb · [EV 15] tapşırıq 1 — post_count əlavə olundu
class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()                    # [EV 15] like_count-un əkizi

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "post_count"]

    def get_post_count(self, category):
        return category.posts.filter(is_published=True).count()


# [EV 14] tələbə yazıb
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # create_user() → password hash-lənir