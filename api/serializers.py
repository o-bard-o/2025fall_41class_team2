# llm_project/api/serializers.py

from rest_framework import serializers
from .models import CustomUser, Project, Document

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # 'username', 'email', 'password' 필드를 사용
        fields = ('username', 'email', 'password')
        # password 필드는 API 응답에 포함되지 않도록 설정 (쓰기 전용)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Serializer의 create 메서드를 오버라이드하여
        # create_user() 함수를 사용 (비밀번호를 해싱하기 위함)
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    



# [!] ProjectSerializer보다 *위에* DocumentSerializer가 오도록 순서 변경
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'original_filename', 'uploaded_at', 'file']

class ProjectSerializer(serializers.ModelSerializer):
    # [!] 1. 이 줄을 추가합니다.
    # (이 프로젝트에 속한 'documents'를 DocumentSerializer로 변환하여 포함)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        # [!] 2. 'documents'를 fields에 추가합니다.
        fields = ['id', 'name', 'created_at', 'documents']