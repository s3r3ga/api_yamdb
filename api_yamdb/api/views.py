from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, User, Comment, Review

from .serializers import (ReviewSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, TitleSerializer)
from .validators import validate_email, validate_username
from .utils import send_mail


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('name', 'year', 'category__slug', 'genre__slug',)

    def perform_create(self, serializer):
        name = self.request.data.get('name')
        year = self.request.data.get('year')
        category_slug = self.request.data.get('category')
        genre_slugs = self.request.data.get('genre')
        name_titles = get_object_or_404(Title, name=name)
        year_titles = get_object_or_404(Title, year=year)
        list_genre = []
        category = get_object_or_404(Category, slug=category_slug)
        for genre_slug in genre_slugs:
            list_genre.append(get_object_or_404(Genre, slug=genre_slug))
        serializer.save(
            category=category,
            genre=list_genre,
            name=name_titles,
            year=year_titles
        )

    def perform_update(self, serializer):
        super(TitleViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        super(TitleViewSet, self).perform_destroy(instance)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


@api_view(['POST'])
def signup_view(request):
    email = request.data.get('email')
    username = request.data.get('username')

    if email is None:
        return Response({'email': 'Email is required.'})

    if not validate_email(email):
        return Response({'email': 'Email is\'n valid.'})

    if username is None:
        return Response({'username': 'Username is required.'})

    if not validate_username(username):
        return Response({'username': f"Incorrect username is '{username}'!"})

    users = User.objects.filter(email=email, username=username)
    if not users.exists():
        User.objects.create(email=email, username=username)

    user = get_object_or_404(User, email=email, username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(user.email, confirmation_code)

    return Response(
        {
            'email': email,
            'username': username,
        }
    )


@api_view(['POST'])
def user_token_view(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    if username is None:
        return Response({'username': 'Username is required.'})

    if not validate_username(username):
        return Response({'username': f"Incorrect username is '{username}'!"})

    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        return Response('Incorrect pair: username - confirmation_code')
    token = AccessToken.for_user(user)
    return Response({'token': str(token)})


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)
