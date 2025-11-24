from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser, Project, Document, Message
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile

class ApiFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'id': str(uuid.uuid4()),
            'username': 'testuser'
        }
        # Create user for authentication in later steps
        self.user = CustomUser.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password='password123',
            id=self.user_data['id']
        )
        self.client.force_authenticate(user=self.user)

    def test_register_user_idempotent(self):
        # Test PUT /api/user
        url = reverse('register')
        data = {
            'email': 'new@example.com',
            'id': str(uuid.uuid4()),
            'username': 'newuser'
        }
        # First call: Create
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)

        # Second call: Update (Idempotent)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.count(), 2)

    def test_project_flow(self):
        # 1. Create Project
        url = reverse('project-list-create')
        data = {'title': 'My Project', 'description': 'Test Description'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_id = response.data['id']

        # 2. Get Project List
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # 3. Get Project Detail
        detail_url = reverse('project-detail', kwargs={'project_id': project_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Project')

        # 4. Upload Document
        doc_url = reverse('document-list-upload', kwargs={'project_id': project_id})
        file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(doc_url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        document_id = response.data['id']

        # 5. List Documents
        response = self.client.get(doc_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # 6. Chat (Send Message)
        chat_url = reverse('message-list-create', kwargs={'project_id': project_id})
        response = self.client.post(chat_url, {'content': 'Hello AI'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'assistant') # Should return AI response

        # 7. Get Message History
        response = self.client.get(chat_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # User msg + AI msg

        # 8. Delete Document
        delete_url = reverse('document-delete', kwargs={'project_id': project_id, 'document_id': document_id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Document.objects.count(), 0)
