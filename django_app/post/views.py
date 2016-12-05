from rest_framework import generics
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from post.models import Post, Comment
from post.serializers import PostListSerializer, PostDetailSerializer, CommentSerializer, PostCreateSerializer
import django_filters


class PostFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Post
        fields = ['hashtags__name', ]


class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = PostFilter


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        pk = request.user.pk
        request.data['author'] = pk
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(hashtags=dict(self.request.data).get('hashtags'))


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def update(self, request, *args, **kwargs):
        if request.user.pk == self.get_object().author.pk:
            request.data['author'] = request.user.pk
            return super().update(request, *args, **kwargs)
        raise AuthenticationFailed(detail="수정 권한이 없습니다.")

    def perform_update(self, serializer):
        serializer.save(hashtags=dict(self.request.data).get('hashtags'))

    def destroy(self, request, *args, **kwargs):
        if request.user.pk == self.get_object().author.pk:
            request.data['author'] = request.user.pk
            return super().destroy(request, *args, **kwargs)
        raise AuthenticationFailed(detail="삭제 권한이 없습니다.")


class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        request.data['author'] = request.user.pk
        request.data['post'] = kwargs.get('pk')
        return super().create(request, *args, **kwargs)

