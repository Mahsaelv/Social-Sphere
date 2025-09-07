from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Thread, Message


# Register your models here.

class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'first_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('date_of_birth', 'bio', 'photo', 'job')}),
    )


def make_deactivation(modeladmin, request, queryset):
    reusult = queryset.update(active=False)
    modeladmin.message_user(request, f"{reusult} Posts were rejected")


make_deactivation.short_description = 'رد پست'


def make_activation(modeladmin, request, queryset):
    reusult = queryset.update(active=True)
    modeladmin.message_user(request, f"{reusult} Posts were accepted")


make_activation.short_description = 'تایید پست'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'created', 'description']
    ordering = ['created']
    search_fields = ['description']
    inlines = [ImageInline]
    actions = [make_deactivation, make_activation]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'created', 'active']
    list_filter = ['active', 'created', 'updated', ]
    search_fields = ['name', 'body']
    list_editable = ['active']
    # autocomplete_fields = ['post']


admin.site.register(Contact)

admin.site.register(Image)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'updated']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'thread', 'sender', 'content', 'timestamp', 'is_read']
    fields = ['thread', 'sender', 'content', 'is_read']
