"""
Custom authentication views for the Assessment Engine.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Login and get authentication token",
    description=(
        "Authenticate with username and password to receive an authentication token. "
        "Use this token in the Authorization header as 'Token <your_token>' for subsequent requests."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "user_id": {"type": "integer"},
                "username": {"type": "string"},
            },
        },
        400: {"description": "Invalid credentials"},
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    
    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        "token": token.key,
        "user_id": user.id,
        "username": user.username,
    })
