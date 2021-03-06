from django.db.models import Count, Prefetch
from django.shortcuts import render, get_object_or_404

from blog.models import Comment, Post, Tag


def serialize_post_optimized(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments__count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts__count,
    }


def get_related_posts_count(tag):
    return tag.posts.count()


def five_most_popular_posts():
    posts = Post.objects.prefetch_author_and_tags()
    popular_posts = posts.popular()
    most_popular_posts = popular_posts[:5].fetch_with_comments_count()
    return most_popular_posts


def index(request):
    posts = Post.objects.prefetch_author_and_tags
    popular_posts = posts.popular()
    most_popular_posts = popular_posts[:5].fetch_with_comments_count()

    fresh_posts = posts.annotate(Count('comments')).order_by('published_at')
    most_fresh_posts = list(fresh_posts)[-5:]

    tags = Tag.objects.all()
    popular_tags = tags.popular()
    most_popular_tags = popular_tags[:5]

    context = {
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post_optimized(post) for post in
                       most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related('author'), slug=slug)
    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': likes.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags.popular()],
    }

    all_tags = Tag.objects.all()
    popular_tags = all_tags.popular()
    most_popular_tags = popular_tags[:5]

    most_popular_posts = five_most_popular_posts()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    all_tags = Tag.objects.all()
    popular_tags = all_tags.popular()
    most_popular_tags = popular_tags[:5]

    most_popular_posts = five_most_popular_posts()

    related_posts = tag.posts.all()[:20].prefetch_related(
        'author',
        Prefetch('tags', queryset=Tag.objects.annotate(Count('posts')))
    ).fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # ?????????? ?????????? ?????????? ?????? ?????? ???????????????????? ?????????????? ???? ?????? ????????????????
    # ?? ?????? ???????????? ??????????????
    return render(request, 'contacts.html', {})
