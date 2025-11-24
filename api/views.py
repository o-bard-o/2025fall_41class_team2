# llm_project/api/views.py

from rest_framework import generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import CustomUser, Project, Document, Message
from .serializers import UserSerializer, ProjectSerializer, DocumentSerializer, MessageSerializer
from .rag_utils import process_and_index_pdf, remove_document_vectors, get_rag_answer

# 1. Authentication
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, *args, **kwargs):
        # Idempotent user registration
        email = request.data.get('email')
        user_id = request.data.get('id')
        username = request.data.get('username')

        if not email or not user_id:
            return Response({"error": "Email and ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, created = CustomUser.objects.get_or_create(
                id=user_id,
                defaults={'email': email, 'username': username or email.split('@')[0]}
            )
            if not created:
                # Update user if exists
                user.email = email
                if username:
                    user.username = username
                user.save()

            # Create or get Django Token for authentication
            token, _ = Token.objects.get_or_create(user=user)
            
            serializer = UserSerializer(user)
            response = Response(
                serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
            # Set token as HttpOnly cookie
            response.set_cookie(
                key='auth_token',
                value=token.key,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=60*60*24*30  # 30 days
            )
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        })

# 2. Projects
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.projects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'project_id'

    def get_queryset(self):
        return self.request.user.projects.all()
    
    def perform_destroy(self, instance):
        # Delete all documents and their vectors before deleting project
        for document in instance.documents.all():
            try:
                remove_document_vectors(document)
            except Exception as e:
                print(f"Error removing vectors for document {document.id}: {e}")
        instance.delete()


# 3. Documents
class DocumentListUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        documents = project.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        file_obj = request.data.get('file')

        if not file_obj:
            return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.create(
            project=project,
            file=file_obj,
            name=file_obj.name,
            status='processing'
        )

        # Trigger RAG indexing (Mocked for now)
        indexing_success = process_and_index_pdf(document)
        
        if indexing_success:
            document.status = 'processed'
            document.save()
            return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
        else:
            document.status = 'failed'
            document.save()
            return Response({"error": "Indexing failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DocumentDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, project_id, document_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        document = get_object_or_404(Document, id=document_id, project=project)

        try:
            remove_document_vectors(document)
            document.file.delete(save=False)
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 4. Chat
class MessageListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        messages = project.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        content = request.data.get('content')

        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save User Message
        user_message = Message.objects.create(
            project=project,
            role='user',
            content=content
        )

        # Get AI Response
        ai_response_content = get_rag_answer(project_id, content)

        # Save AI Message
        ai_message = Message.objects.create(
            project=project,
            role='assistant',
            content=ai_response_content
        )

        return Response(MessageSerializer(ai_message).data, status=status.HTTP_200_OK)