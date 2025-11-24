# llm_project/api/serializers.py

from rest_framework import serializers
from .models import CustomUser, Project, Document, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password') # Added id
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data.get('username'), # Use .get() as username might be optional
            email=validated_data['email'],
            password=validated_data.get('password'), # Password might not be provided in some flows? Spec says PUT /user
            id=validated_data.get('id') # Allow setting ID manually
        )
        return user

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'status', 'created_at', 'file'] # original_filename -> name, added status

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'documents'] # name -> title, added description, updated_at