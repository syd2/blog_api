from rest_framework.serializers import ModelSerializer
from .models import Post, Comment
from rest_framework import serializers


class CommentSerializer(ModelSerializer):
    owner_name = serializers.SerializerMethodField('get_owner_name')
    class Meta:
        model = Comment
        fields = ('id', 'owner_name', 'text')
        read_only_fields = ('owner_name',)

    def get_owner_name(self, comment):
        try:
            return comment.owner.username
        except:
            return


class PostSerializer(ModelSerializer):
    comments = CommentSerializer(many=True, required=False)
    author_name = serializers.SerializerMethodField('get_author_name', read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'author_name', 'title', 'body', 'created', 'comments')
        read_only_fields = ('author_name',)

    def get_author_name(self, post):
        try:
            return post.author.username
        except:
            return