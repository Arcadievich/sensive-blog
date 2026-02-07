from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Prefetch, Count


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.num_comments,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags_with_counts],
        'first_tag_title': post.tags_with_counts[0].title if post.tags_with_counts else '',
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_posts,
    }


def index(request):

    most_popular_posts = (
        Post.objects
        .popular()
        .select_related('author')
        .with_tags_with_counts()
        [:5]
        .fetch_with_comments_count()
    )

    most_fresh_posts = (
        Post.objects
        .order_by('-published_at')
        .select_related('author')
        .with_tags_with_counts()
        .annotate(num_comments=Count('comments'))
    )[:5]

    most_popular_tags = Tag.objects.with_posts_count().order_by('-num_posts')[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):

    post = (
        Post.objects
        .select_related('author')
        .with_tags_with_counts()
        .prefetch_related(
            Prefetch('comments', queryset=Comment.objects.select_related('author'))
        )
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
        .get(slug=slug)
    )

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': [
            {
                'text': comment.text,
                'published_at': comment.published_at,
                'author': comment.author.username,
            }
            for comment in post.comments.all()
        ],
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags_with_counts],
    }

    most_popular_tags = Tag.objects.with_posts_count().order_by('-num_posts')[:5]

    most_popular_posts = (
        Post.objects
        .popular()
        .select_related('author')
        .with_tags_with_counts()
        [:5]
        .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.with_posts_count().get(title=tag_title)

    most_popular_tags = Tag.objects.with_posts_count().order_by('-num_posts')[:5]

    most_popular_posts = (
        Post.objects
        .popular()
        .select_related('author')
        .with_tags_with_counts()
        [:5]
        .fetch_with_comments_count()
    )

    related_posts = (
        tag.posts
        .select_related('author')
        .with_tags_with_counts()
        .annotate(num_comments=Count('comments'))
        .order_by('-published_at')[:20]
    )

    context = {
        'tag': tag.title,
        'posts_with_tag': tag.num_posts,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
