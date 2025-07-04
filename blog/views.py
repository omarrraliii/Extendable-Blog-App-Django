from django.http import Http404
from django.shortcuts import render , get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

# Create your views here.



def post_search(request):
    results= []
    query= None
    form=SearchForm()
    if 'query' in request.GET:
        form=SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector= SearchVector('title', weight='A')+\
            #                SearchVector('body', weight= 'B')
            # search_query = SearchQuery(query)
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title',query))\
                    .filter(similarity__gt=0.1)\
                        .order_by('-similarity')
    return render (request,'blog/post/search.html',
                   {'form':form,
                    'query': query,
                    'results': results})
            

@require_POST
def post_comment(request, post_id):
    post= get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED) 
    form=CommentForm(data=request.POST)
    comment=None
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post=post
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post':post,
                   'form':form,
                   'comment': comment})

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
# class PostListView(ListView):
#     queryset = Post.published.all()                               #ListView for displaying the posts
#     context_object_name= 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):                                                 #View for listing all the posts
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])                        
    paginator=Paginator(post_list, 3)                                          
    page_number = request.GET.get('page',1)
    try:
        posts=paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)                                          #Getting the page number from the request
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'tag': tag,})

def post_details(request,year,month,day,post):                                           #View for displaying the details of a post
    post = get_object_or_404(Post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             slug=post,
                             status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form =CommentForm()         

    #List of similar posts
    post_tag_ids= post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tag_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                  .order_by('-same_tags','-publish')[:4]
    return render(request,
                  'blog/post/details.html',
                  {'post':post, 
                   'form':form,
                   'comments': comments,
                   'similar_posts': similar_posts})