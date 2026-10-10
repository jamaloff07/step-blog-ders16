from django.contrib import admin

from .models import Post, Category, Tag, Comment, ContactMessage


# [DƏRS 10] şərhlər postun admin səhifəsinin içində görünür
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1                                                     # neçə boş sətir göstərilsin


# [DƏRS 9] müəllim yazıb
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "is_published", "is_featured", "views"]
    list_filter = ["is_published", "is_featured", "category"]     # category indi ForeignKey-dir — filtr yenə işləyir
    search_fields = ["title", "content"]
    list_editable = ["is_published", "is_featured"]               # [EV 9] bonus
    inlines = [CommentInline]                                     # [DƏRS 10]
    filter_horizontal = ["tags"]                                  # [PRAKTİKA 10] teq seçmək üçün rahat iki pəncərə
    actions = ["make_featured"]                                   # [REFERANS 9] — tələbəyə verilmir

    @admin.action(description="Seçilmiş et")
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)


# [PRAKTİKA 9] tələbə yazıb
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}                      # ad yazdıqca slug özü dolur


# [PRAKTİKA 10] tələbə yazır — CategoryAdmin-in əkizi
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


# [DƏRS 10] dərsdə sadəcə admin.site.register(Comment) yazılır.
# [REFERANS 10] — tam CommentAdmin (tələbəyə verilmir)
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "parent", "is_active", "created_at"]   # [EV 12] tapşırıq 1 — name → author
    list_filter = ["is_active", "post"]
    search_fields = ["text"]
    list_editable = ["is_active"]                                 # şərhi cədvəldən gizlət / göstər


# [REFERANS 11] — əlaqə mesajlarını admin oxuyur
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "created_at"]
