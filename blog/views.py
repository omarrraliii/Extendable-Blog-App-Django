from django.http import Http404
from django.shortcuts import render , get_object_or_404
from .models import Post

# Create your views here.

def post_list(request):                                                 #View for listing all the posts
    posts = Post.published.all()
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})

def post_details(request,id):                                           #View for displaying the details of a post
    post = get_object_or_404(Post,
                             id=id,
                             status=Post.Status.PUBLISHED)
    return render(request,
                  'blog/post/details.html',
                  {'post':post})