from django import forms

from .models import Post, Comment, Category

# Form üç iş görür: 1) HTML input-ları çəkir  2) gələn məlumatı yoxlayır  3) (ModelForm) bazaya yazır.
# Nişanlar:  [DƏRS 12] müəllim · [DƏRS 12] praktikadan sonra müəllim · [PRAKTİKA 12] tələbə · [EV 12] tapşırıq 1–3 / bonus · [REFERANS 12] tələbəyə verilmir


# [DƏRS 11] ModelForm — sahələri Comment modelindən özü götürür
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment                                           # hansı model üçün
        fields = ["text"]                                         # [EV 12] tapşırıq 2 — "name" getdi: müəllifi view yazır
        labels = {"text": "Şərhin"}

    # [DƏRS 11] öz yoxlama qaydamız: clean_<sahə adı>. Django bunu is_valid() zamanı özü çağırır
    def clean_text(self):
        text = self.cleaned_data["text"]                          # bu sahənin təmizlənmiş dəyəri
        if len(text) < 5:
            raise forms.ValidationError("Şərh ən azı 5 simvol olmalıdır.")
        return text                                               # HƏMİŞƏ dəyəri qaytar

    # [EV 11]-dəki clean_name silindi — name sahəsi artıq yoxdur ([EV 12] tapşırıq 1)


# [DƏRS 11] post yaratmaq və redaktə etmək üçün — eyni form hər ikisinə yarayır
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # [DƏRS 12] "author" formdan ÇIXARILDI — müəllifi istifadəçi seçmir, view request.user yazır
        # [REFERANS 12] — is_published: qaralama kimi saxlamaq üçün
        fields = ["title", "category", "tags", "content", "image", "is_published"]
        labels = {
            "title": "Başlıq",
            "category": "Kateqoriya",
            "tags": "Teqlər",
            "content": "Mətn",
            "image": "Şəkil",
            "is_published": "Dərc olunsun",
        }

    # [EV 11] bonus
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise forms.ValidationError("Başlıq ən azı 5 simvol olmalıdır.")
        if title.isupper():
            raise forms.ValidationError("Başlığı tam böyük hərflə yazma.")
        return title


# [REFERANS 11] — PostForm-un əkizi
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "description"]


# [REFERANS 11] — adi Form: modelə bağlı deyil, sahələri özümüz yazırıq
class ContactForm(forms.Form):
    name = forms.CharField(max_length=50, label="Adın")
    email = forms.EmailField(label="Email")                       # email formatını özü yoxlayır
    message = forms.CharField(widget=forms.Textarea, label="Mesaj")

    def clean_message(self):
        message = self.cleaned_data["message"]
        if len(message) < 10:
            raise forms.ValidationError("Mesaj ən azı 10 simvol olmalıdır.")
        return message
