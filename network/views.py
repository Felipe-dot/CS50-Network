from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

import json

from .models import User, Post, Like, Follow

def index(request):
    posts_list = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    liked_posts_ids = []
    if request.user.is_authenticated:
        liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "liked_posts_ids": liked_posts_ids
    })

@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            post = Post(user=request.user, content=content)
            post.save()
        return HttpResponseRedirect(reverse("index"))
    return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "network/index.html", {
            "message": "User not found."
        })
    
    if request.method == "POST":
        if request.user.is_authenticated and request.user != profile_user:
            action = request.POST.get("action")
            if action == "follow":
                Follow.objects.get_or_create(follower=request.user, following=profile_user)
            elif action == "unfollow":
                Follow.objects.filter(follower=request.user, following=profile_user).delete()
            return HttpResponseRedirect(reverse('profile', args=[username]))
    
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    posts_list = profile_user.posts.all().order_by("-timestamp")
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    liked_posts_ids = []
    if request.user.is_authenticated:
        liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "page_obj": page_obj,
        "liked_posts_ids": liked_posts_ids
    })

@login_required
def following(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts_list = Post.objects.filter(user__in=following_users).order_by("-timestamp")
    
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "liked_posts_ids": liked_posts_ids
    })

@login_required
def edit_post(request, post_id):
    if request.method == "PUT" or request.method == "POST":
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        
        if post.user != request.user:
            return JsonResponse({"error": "Unauthorized."}, status=403)
        
        data = json.loads(request.body)
        new_content = data.get("content", "").strip()
        if new_content:
            post.content = new_content
            post.save()
            return JsonResponse({"message": "Post updated successfully.", "content": post.content})
        else:
            return JsonResponse({"error": "Content cannot be empty."}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=400)

@login_required
def toggle_like(request, post_id):
    if request.method == "PUT" or request.method == "POST":
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        
        like_exists = Like.objects.filter(user=request.user, post=post).exists()
        
        if like_exists:
            Like.objects.filter(user=request.user, post=post).delete()
            action = "unliked"
        else:
            Like.objects.create(user=request.user, post=post)
            action = "liked"
        
        return JsonResponse({"message": f"Post {action}.", "likes_count": post.likes.count(), "action": action})
    return JsonResponse({"error": "Invalid request method."}, status=400)
