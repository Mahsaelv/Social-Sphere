from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from .views import inbox_view, thread_detail_view
from .forms import CustomPasswordChangeForm


app_name = 'social'

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(
        authentication_form=LoginForm,
        template_name='auth/login.html'
    ), name="login"),
    path('logout/', views.log_out, name="logout"),
    path('register/', views.register, name="register"),
    path('activate/<uidb64>/<token>/', views.activate_account, name="activate"),

    # Password Management
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='auth/password_change.html',
        success_url=reverse_lazy('social:password_change_done'),
        form_class=CustomPasswordChangeForm
    ), name="password_change"),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='auth/password_change_done.html'
    ), name="password_change_done"),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset_form.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt',
        html_email_template_name='auth/password_reset_email.html',
        success_url='done'
    ), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name="password_reset_done"),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url='/password-reset/complete'
    ), name="password_reset_confirm"),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name="password_reset_complete"),

    # Account
    path('user/edit', views.edit_user, name="edit_account"),
    path('users/<username>/', views.profile_view, name='user_detail'),

    # User
    path('users/', views.user_list, name='user_list'),
    path('users/<username>/', views.profile_view, name='profile'),
    path('users/<username>/<rel>', views.contact, name='user_contact'),
    path('follow/', views.user_follow, name='user_follow'),
    path('search/', views.search_users, name='search'),

    # Profile AJAX
    path('users/<username>/posts/', views.profile_posts_ajax, name='profile-posts-ajax'),
    path('users/<username>/saved/', views.profile_saved_ajax, name='profile-saved-ajax'),
    path('users/<username>/followers-ajax/', views.profile_followers_ajax, name='profile-followers-ajax'),
    path('users/<username>/following-ajax/', views.profile_following_ajax, name='profile-following-ajax'),

    # Post
    path('posts/', views.post_list, name="post_list"),
    path('posts/post/<slug:tag_slug>/', views.post_list, name="post_list_by_tag"),
    path('posts/create_post/', views.create_post, name="create_post"),
    path('posts/detail/<pk>', views.post_detail, name="post_detail"),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('posts/<post_id>/comment', views.post_comment, name="post_comment"),
    path('like_post/', views.like_post, name='like_post'),
    path('save-post/', views.save_post, name='save_post'),

    # Explore & Notifications
    path('explore/', views.explore, name='explore'),
    path('explore/tag/<slug:tag_slug>/', views.explore, name='explore_by_tag'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),

    # Chat
    path('inbox/', inbox_view, name='inbox'),
    path('inbox/<int:thread_id>/', thread_detail_view, name='thread-detail'),
]
