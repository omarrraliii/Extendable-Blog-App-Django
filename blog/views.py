from django.http import Http404
from django.shortcuts import render , get_object_or_404
from .models import Post
from django.core.paginator import Paginator

# Create your views here.

def post_list(request):                                                 #View for listing all the posts
    post_list = Post.published.all()
    paginator=Paginator(post_list, 3)                                          #Pagination of posts
    page_number = request.GET.get('page',1)
    posts=paginator.page(page_number)                                          #Getting the page number from the request
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})

def post_details(request,year,month,day,post):                                           #View for displaying the details of a post
    post = get_object_or_404(Post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             slug=post,
                             status=Post.Status.PUBLISHED)
    return render(request,
                  'blog/post/details.html',
                  {'post':post})