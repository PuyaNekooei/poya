from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from .permissions import role_of


def user_payload(user):
    """Common user representation returned by auth endpoints, including role."""
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': role_of(user),
        'roles': list(user.groups.values_list('name', flat=True)),
        'is_admin': role_of(user) == 'admin',
    }


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'نام کاربری و رمز عبور الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': user_payload(user),
                'message': 'ورود موفقیت‌آمیز بود'
            })
        else:
            return Response({
                'error': 'نام کاربری یا رمز عبور اشتباه است'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Delete the token
            request.user.auth_token.delete()
            logout(request)
            return Response({
                'message': 'خروج موفقیت‌آمیز بود'
            })
        except Exception as e:
            return Response({
                'error': 'خطا در خروج از سیستم'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not username or not password:
            return Response({
                'error': 'نام کاربری و رمز عبور الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'این نام کاربری قبلاً استفاده شده است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': user_payload(user),
                'message': 'حساب کاربری با موفقیت ایجاد شد'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'خطا در ایجاد حساب کاربری'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            **user_payload(user),
            'date_joined': user.date_joined,
        })
    
    def put(self, request):
        user = request.user
        
        # Update user fields
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            user.email = request.data['email']
        
        user.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'message': 'اطلاعات کاربر با موفقیت بروزرسانی شد'
        })
