

# Create your views here.
#users/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    """
    form = UserCreationForm(request.data)
    
    if form.is_valid():
        user = form.save()
        return Response({
            'message': f'Account created for {user.username}! You can now login.',
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'errors': form.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint (for session-based auth)
    Note: For production, consider using JWT tokens instead
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        from django.contrib.auth import login
        login(request, user)
        return Response({
            'message': 'Login successful.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return Response(
        {'error': 'Invalid username or password.'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint
    """
    from django.contrib.auth import logout
    logout(request)
    return Response({'message': 'Logout successful.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get current authenticated user info
    """
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'date_joined': request.user.date_joined
    })
