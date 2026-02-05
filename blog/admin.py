from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ['likes', 'tags']


class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ['author']
    list_display = ['post__title', 'author__username', 'text', 'published_at']


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment, CommentAdmin)
