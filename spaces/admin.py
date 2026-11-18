from django.contrib import admin

from .models import Space, Testimonial


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "theme", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug", "owner__username")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "space", "status", "rating", "created_at")
    list_filter = ("status", "space")
    search_fields = ("name", "email", "body")
