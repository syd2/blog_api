from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from .serializers import PostSerializer, CommentSerializer
from rest_framework.authentication import TokenAuthentication

# Create your views here.
@api_view(['GET', ])
def post_list(request):
    #anonymous can too
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['POST', ])
@permission_classes((permissions.IsAuthenticated,))
def post_create(request):
    #only authors and  authenticated users
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
    return Response(serializer.data)


@api_view(['GET', ])
def post_detail(request, id):
    #anonymouous user can acces
    post = get_object_or_404(Post, id=id)
    serializer = PostSerializer(post, many=False)
    return Response(serializer.data)


class PostComment(APIView):
    #authenticated users
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            text = serializer.data.get('text')
            post = get_object_or_404(Post, pk=pk)
            queryset = Comment.objects.filter(text=text)
            if queryset.exists():
                comment = queryset[0]
                comment.owner = request.user #the current user
                comment.text = text
                comment.post = post
                comment.save(update_fields=['text'])
                return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
            else:
                comment = Comment(post=post, owner=request.user, text=text)
                comment.save()
                return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response({'Bad Request': 'invalid data ...'}, status=status.HTTP_400_BAD_REQUEST)


class DetailPostComment(APIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get(self, request, pk, comment_pk):
        post = get_object_or_404(Post, pk=pk)
        comment = get_object_or_404(Comment, pk=comment_pk, post=post)
        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data)

    def delete(self, request, pk, comment_pk):

        post = get_object_or_404(Post, pk=pk)
        comment = get_object_or_404(Comment, post=post, pk=comment_pk)
        if comment.owner != request.user:
            return Response({'error': 'you are not the author of this post'}, status=status.HTTP_403_FORBIDDEN)
        else:
            comment.delete()
            return Response('successfully deleted', status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, comment_pk):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            text = serializer.data.get('text')
            post = get_object_or_404(Post, pk=pk)
            queryset = Comment.objects.filter(post=post, pk=comment_pk)
            if queryset.exists():
                comment = queryset[0]
                comment.owner = request.user
                comment.text = text
                comment.post = post
                comment.save(update_fields=['text'])
                return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
            return Response({'Not found': 'comment doesnt exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
@permission_classes((permissions.IsAuthenticated, ))
def post_delete(request, id):
    #author, authenticated
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:#checking if user is author
        return Response({'error': 'you are not the author of this post'}, status=status.HTTP_403_FORBIDDEN)
    else:
        post.delete()
        return Response('successfully deleted', status=status.HTTP_204_NO_CONTENT)


class PostUpdate(APIView):
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    #author and authenticated
    def patch(self, request, pk):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            title = serializer.data.get('title')
            body = serializer.data.get('body')
            queryset = Post.objects.filter(pk=pk)
            if queryset.exists():
                post = queryset[0]
                if post.author != request.user:
                    return Response({'error': 'you are not the author of this post'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    post.title = title
                    post.body = body
                    post.author = request.user
                    post.save(update_fields=['title', 'body'])
                    return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
            return Response('Not found', status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad request': 'invalid data'}, status=status.HTTP_400_BAD_REQUEST)
