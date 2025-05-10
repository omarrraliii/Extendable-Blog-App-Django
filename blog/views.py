from django.http import Http404
from django.shortcuts import render , get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail

# Create your views here.

def post_share(request, post_id):
    sent=False
    post=get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)  
    if request.method == 'POST':
        form=EmailPostForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            post_url=request.build_absolute_uri(
                post.get_absolute_url())
            subject=f"{cd['name']} recommends you to read " \
                    f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message,'dummy@gmail.com',
                      [cd['to']])
            sent=True  
    else:
        form=EmailPostForm()
    return render(request, 'blog/post/share.html',{'post': post,
                                                   'form': form,
                                                   'sent': sent})
class PostListView(ListView):
    queryset = Post.published.all()                               #ListView for displaying the posts
    context_object_name= 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

# def post_list(request):                                                 #View for listing all the posts
#     post_list = Post.published.all()
#     paginator=Paginator(post_list, 3)                                          
#     page_number = request.GET.get('page',1)
#     try:
#         posts=paginator.page(page_number)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     except EmptyPage:
#         posts - paginator.page(paginator.num_pages)                                          #Getting the page number from the request
#     return render(request,
#                   'blog/post/list.html',
#                   {'posts': posts})

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