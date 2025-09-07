from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Post, Contact, Image
from taggit.models import Tag
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.timezone import now
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from .tokens import ShortLivedActivationTokenGenerator
import json
from base64 import urlsafe_b64encode, urlsafe_b64decode


activation_token_generator = ShortLivedActivationTokenGenerator()

User = get_user_model()


def log_out(request):
    logout(request)
    return redirect('social:login')

def index(request):
    if request.user.is_authenticated:
        return redirect('social:post_list')
    return redirect('social:login')

def profile(request):
    try:
        user = User.objects.prefetch_related('followers', 'following').get(id=request.user.id)
    except:
        return redirect('social:login')
    saved_posts = user.saved_posts.all()[:7]
    my_posts = user.user_posts.all()[:8]
    following = user.get_followings()
    followers = user.get_followers()
    conntext = {
        'saved_posts': saved_posts,
        'my_posts': my_posts,
        'user': user,
        'following': following,
        'followers': followers,
    }
    return render(request, 'user/profile.html', conntext)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # تا وقتی ایمیل فعال نشه
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            activation_link = request.build_absolute_uri(
                reverse('social:activate', kwargs={'uidb64': uid, 'token': token})
            )

            subject = "Activate your account"
            html_message = render_to_string('auth/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            email = EmailMultiAlternatives(subject, html_message, to=[user.email])
            email.attach_alternative(html_message, "text/html")
            email.send()

            messages.success(request, "Check your email to activate your account.")
            return redirect('social:login')
        else:
            return render(request, 'auth/register.html', {'form': form})

    else:
        form = UserRegisterForm()
        return render(request, 'auth/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated.")
        return redirect('social:post_list')
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect('social:register')


@login_required
def edit_user(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user, files=request.FILES)
        if user_form.is_valid():
            user_form.save()
        return redirect('social:profile', request.user.username)
    else:
        user_form = UserEditForm(instance=request.user)
    context = {
        'user_form': user_form
    }
    return render(request, 'user/edit_user.html', context=context)


@login_required
def post_list(request, tag_slug=None):
    qs = Post.objects.select_related('author').order_by('-total_likes')
    following_ids = request.user.following.values_list('id', flat=True)
    qs = qs.filter(author__id__in=following_ids)

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        qs = qs.filter(tags__in=[tag])

    page = request.GET.get('page')
    paginator = Paginator(qs, 3)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = []

    recent_contacts = (
        Contact.objects
            .filter(user_from=request.user)
            .select_related('user_to')
            .order_by('-created')[:10]
    )
    followings = [c.user_to for c in recent_contacts]

    exclude_ids = list(following_ids) + [request.user.id]
    suggestions = User.objects.exclude(id__in=exclude_ids).order_by('?')[:5]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'post/feed_ajax.html', {'posts': posts})

    return render(request, 'post/feed.html', {
        'posts': posts,
        'tag': tag,
        'followings': followings,
        'suggestions': suggestions,
    })


@login_required
def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect('social:profile', username=request.user.username)
    else:
        form = CreatePostForm()
    return render(request, 'post/create.html', {'form': form})


@login_required
def post_detail(request, pk):
    # بارگذاری پست و پست‌های مشابه بر اساس تگ
    post = get_object_or_404(Post, id=pk)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = (
        Post.objects
            .filter(tags__in=post_tags_ids)
            .exclude(id=post.id)
            .annotate(same_tags=Count('tags'))
            .order_by('-same_tags', '-created')[:4]
    )

    form = CommentForm()

    context = {
        'post': post,
        'similar_posts': similar_posts,
        'form': form,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'post/detail_model.html', context)

    return render(request, 'post/detail.html', context)


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        if liked:
            Notification.objects.create(
                user=post.author,
                actor=request.user,
                verb="liked your post",
                target=post
            )
        post_likes_count = post.likes.count()
        response_data = {
            'liked': liked,
            'likes_count': post_likes_count,
        }
    else:
        response_data = {'error': 'Invalid post_id'}

    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = Post.objects.get(id=post_id)
        user = request.user

        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True

        return JsonResponse({'saved': saved})
    return JsonResponse({'error': 'Invalid request'})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'user/user_list.html', {'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'user/user_detail.html', {'user': user})


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                follow = True
                if follow:
                    Notification.objects.create(
                        user=user,
                        actor=request.user,
                        verb="started following you"
                    )
            following_count = user.following.count()
            followers_count = user.followers.count()

            return JsonResponse({'follow': follow, 'following_count': following_count,
                                 'followers_count': followers_count})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist.'})

    return JsonResponse({'error': 'Invalid request.'})


def contact(request, username, rel):
    user = User.objects.get(username=username)
    if rel == 'following':
        users = user.get_followings()
    else:
        users = user.get_followers()
    return render(request, 'user/user_list.html', {'users': users})


@login_required
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.name = request.user.first_name or request.user.username
        comment.save()
        Notification.objects.create(
            user=post.author,
            actor=request.user,
            verb="commented on your post",
            target=post
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'name': comment.name,
                'body': comment.body,
                'user_photo': request.user.photo.url if getattr(request.user, 'photo', None) else None,
                'created': 'just now',
            })

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(next_url)


@login_required
def inbox_view(request):
    user = request.user
    start = request.GET.get('start')
    post_id = request.GET.get('post')
    selected_thread = None
    selected_partner = None

    if start:
        other = get_object_or_404(User, id=start)
        thread = (Thread.objects
                  .filter(participants=user)
                  .filter(participants=other)
                  .first())
        if not thread:
            thread = Thread.objects.create()
            thread.participants.add(user, other)
        selected_thread = thread
        selected_partner = thread.participants.exclude(id=user.id).first()
        thread.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    if selected_thread and post_id:
        post_obj = get_object_or_404(Post, id=post_id)
        Message.objects.create(thread=selected_thread,
                               sender=user,
                               shared_post=post_obj)
        return redirect(f"{reverse('social:inbox')}?start={start}")

    threads = (Thread.objects
               .filter(participants=user)
               .order_by('-updated')
               .prefetch_related('participants', 'messages__sender', 'messages__shared_post'))
    threads_data = []
    for thread in threads:
        partner = thread.participants.exclude(id=user.id).first()
        unread = thread.messages.filter(is_read=False).exclude(sender=user).count()
        threads_data.append({
            'thread': thread,
            'partner': partner,
            'unread_count': unread,
        })

    messages = selected_thread.messages.order_by('timestamp') if selected_thread else []

    return render(request, 'chat/inbox.html', {
        'threads_data': threads_data,
        'selected_thread': selected_thread,
        'partner': selected_partner,
        'messages': messages,
    })


@login_required
def thread_detail_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    user = request.user
    if user not in thread.participants.all():
        return redirect('social:inbox')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                thread=thread,
                sender=user,
                content=content
            )
            thread.updated = now()
            thread.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'sender_photo': user.photo.url if getattr(user, 'photo', None) else '',
                    'content': msg.content,
                    'timestamp': msg.timestamp.strftime('%I:%M %p'),
                    'is_mine': True,
                })
        return redirect('social:thread-detail', thread_id=thread.id)


    thread.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    post_id = request.GET.get('post')
    if post_id:
        post_obj = get_object_or_404(Post, id=post_id)
        Message.objects.create(
            thread=thread,
            sender=user,
            shared_post=post_obj
        )
        return redirect('social:thread-detail', thread_id=thread.id)

    messages = thread.messages.order_by('timestamp').select_related('sender', 'shared_post')
    partner = thread.participants.exclude(id=user.id).first()

    return render(request, 'chat/thread_detail.html', {
        'thread': thread,
        'messages': messages,
        'partner': partner,
        'selected_thread': thread,
    })


@login_required
def explore(request, tag_slug=None):
    posts = Post.objects.select_related('author').order_by('-created')
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    q = request.GET.get('q', '').strip()
    if q:
        matching_tags = Tag.objects.filter(name__icontains=q)
        posts = posts.filter(tags__in=matching_tags).distinct()

    return render(request, 'post/explore.html', {
        'posts': posts,
        'tag': tag,
        'q': q,
    })


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    if query:
        users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.none()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'search/results_ajax.html', {'users': users})

    return render(request, 'search/search.html', {
        'users': users,
        'query': query,
    })


@login_required
def notifications(request):
    Notification.objects.filter(user=request.user, unread=True).update(unread=False)

    notifs = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'post/notifications.html', {
        'notifications': notifs
    })


@login_required
@require_POST
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.unread = False
    notif.save()
    return JsonResponse({'success': True})


@login_required
def profile_view(request, username):
    user_obj = get_object_or_404(User, username=username, is_active=True)
    is_self = (request.user == user_obj)
    return render(request, 'user/profile.html', {
        'user': user_obj,
        'is_self': is_self,
        'followers': user_obj.get_followers(),
        'following': user_obj.get_followings(),
    })


@login_required
def profile_posts_ajax(request, username):
    """Returns a page of this user’s posts as HTML snippets."""
    user_obj = get_object_or_404(User, username=username, is_active=True)
    qs = user_obj.user_posts.all().order_by('-created')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        posts = paginator.page(page)
    except:
        posts = []
    return render(request, 'user/_post_grid_ajax.html', {'posts': posts})


@login_required
def profile_saved_ajax(request, username):
    """Returns a page of this user’s saved posts."""
    user_obj = get_object_or_404(User, username=username, is_active=True)
    qs = user_obj.saved_posts.all().order_by('-created')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        posts = paginator.page(page)
    except:
        posts = []
    return render(request, 'user/_post_grid_ajax.html', {'posts': posts})


@login_required
def profile_followers_ajax(request, username):
    """Returns JSON list of followers for the modal."""
    user_obj = get_object_or_404(User, username=username, is_active=True)
    data = []
    for u in user_obj.get_followers():
        data.append({
            'username': u.username,
            'full_name': u.get_full_name() or u.username,
            'photo_url': u.photo.url if u.photo else '',
        })
    return JsonResponse({'users': data})


@login_required
def profile_following_ajax(request, username):
    """Returns JSON list of followings for the modal."""
    user_obj = get_object_or_404(User, username=username, is_active=True)
    data = []
    for u in user_obj.get_followings():
        data.append({
            'username': u.username,
            'full_name': u.get_full_name() or u.username,
            'photo_url': u.photo.url if u.photo else '',
        })
    return JsonResponse({'users': data})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    images = post.images.all()
    images_count = images.count()
    if request.method == 'POST':
        form = EditPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.save()
            form.save_m2m()
            for idx, img_field in enumerate(['image1', 'image2'], start=0):
                new_file = form.cleaned_data.get(img_field)
                if new_file:
                    if idx < images_count:
                        # replace existing
                        old_img = images[idx]
                        old_img.image_file.delete(save=False)
                        old_img.image_file = new_file
                        old_img.save()
                    else:
                        # add new
                        Image.objects.create(post=updated, image_file=new_file)
            return redirect('social:post_detail', pk=updated.pk)
    else:
        form = EditPostForm(instance=post)
    return render(request, 'post/edit.html', {
        'post': post,
        'form': form,
        'images': images,
        'images_count': images_count,
    })

@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    return redirect('social:profile', username=request.user.username)
