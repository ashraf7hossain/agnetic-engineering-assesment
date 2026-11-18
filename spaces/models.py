from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Space(models.Model):
    class Theme(models.TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="spaces",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    logo_url = models.URLField(blank=True)
    header_title = models.CharField(max_length=200)
    message = models.TextField()
    collect_ratings = models.BooleanField(default=True)
    theme = models.CharField(
        max_length=10,
        choices=Theme.choices,
        default=Theme.LIGHT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("spaces:detail", kwargs={"slug": self.slug})

    def get_collect_url(self):
        return reverse("spaces:collect", kwargs={"slug": self.slug})

    def get_wall_url(self):
        return reverse("spaces:wall", kwargs={"slug": self.slug})

    def get_inbox_url(self):
        return reverse("spaces:inbox", kwargs={"slug": self.slug})


class Testimonial(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="testimonials",
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    body = models.TextField(max_length=2000)
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    consent = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.status}) — {self.space.slug}"
