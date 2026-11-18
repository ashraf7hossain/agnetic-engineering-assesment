from django import forms
from django.utils.text import slugify

from .models import Space, Testimonial


class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = [
            "name",
            "slug",
            "logo_url",
            "header_title",
            "message",
            "collect_ratings",
            "theme",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Acme Inc"}),
            "slug": forms.TextInput(attrs={"placeholder": "acme"}),
            "logo_url": forms.URLInput(attrs={"placeholder": "https://…"}),
            "header_title": forms.TextInput(
                attrs={"placeholder": "Share your experience with Acme"}
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us how our product helped you.",
                }
            ),
        }

    def clean_slug(self):
        slug = slugify(self.cleaned_data["slug"])
        if not slug:
            raise forms.ValidationError("Enter a valid slug.")
        qs = Space.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("That slug is already taken.")
        return slug


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "email", "body", "rating", "consent"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "body": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Write your testimonial…",
                }
            ),
            "rating": forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
        }

    def __init__(self, *args, space: Space | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.space = space
        if space and not space.collect_ratings:
            self.fields.pop("rating", None)
        self.fields["consent"].required = True

    def clean_consent(self):
        consent = self.cleaned_data.get("consent")
        if not consent:
            raise forms.ValidationError(
                "You must consent to publish this testimonial."
            )
        return consent

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if self.space and not self.space.collect_ratings:
            return None
        return rating
