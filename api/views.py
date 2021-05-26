from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import ModelFilter
from .models import Category, Genre, Review, Title
from .permissions import GeneralPermission, ReviewsPermission
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleGeneralSerializer, TitleSlugSerializer)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    permission_classes = [GeneralPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    permission_classes = [GeneralPermission]

    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filter_class = ModelFilter
    permission_classes = [GeneralPermission]
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleSlugSerializer
        return TitleGeneralSerializer


class ReviewViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ReviewsPermission]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user,
                        title=title)


class CommentViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ReviewsPermission]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user,
                        review=review)
