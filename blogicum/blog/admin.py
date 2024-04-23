from django.contrib import admin

from .models import Category, Location, Post, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'created_at'
    )


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created_at'
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'created_at'
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'created_at',
        'author'
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
