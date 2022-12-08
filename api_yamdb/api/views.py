from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    decorators, filters, mixins, permissions, response, status, viewsets
)
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import (
    Category, Genre, Review, Title, User,
)

from .filters import TitleFilter
from .paginators import CustomPagination
from .permissions import (
    IsAdmin, IsAdminUserOrReadOnly, IsStaffOrAuthorOrReadOnly
)
from .serializers import (
    ReviewSerializer, CommentSerializer, GenreSerializer,
    CategorySerializer, SignUpSerializer, UserSerializer, TitleReadSerializer,
    TitleWriteSerializer
)
from .utils import send_mail

User = get_user_model()


class CLDViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    pass


class CategoryViewSet(CLDViewSet):
    queryset = Category.objects.all()
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = CustomPagination


class GenreViewSet(CLDViewSet):
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = CustomPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by('-id').annotate(Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title

    def get_queryset(self):
        title = self._get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self._get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def _get_review(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        return review

    def get_queryset(self):
        review = self._get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    permission_classes = (IsAdmin,)
    pagination_class = CustomPagination

    @decorators.action(
        methods=['patch', 'get'], detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='me', url_name='me')
    def me(self, request):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                instance, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return response.Response(serializer.data)


class OnlyCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    pass


class SignUpViewSet(OnlyCreateViewSet):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        data = {
            'username': request.data.get('username'),
            'email': request.data.get('email')
        }
        serializer = self.get_serializer(data=data)
        if not self.queryset.filter(**data).exists():
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        user = get_object_or_404(User, **data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(user.email, confirmation_code)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class JWTUserViewSet(OnlyCreateViewSet):
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        if username is None or confirmation_code is None:
            return response.Response(
                'Incorrect input', status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return response.Response(
                'Incorrect pair: username - confirmation_code',
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return response.Response(
            {'token': str(token)},
            status=status.HTTP_200_OK
        )
