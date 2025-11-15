# users/views/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers.user_serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.permissions import AllowAny

# Swagger Examples
registration_example = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, example='diksha'),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='diksha'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='sapkal'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, example='diksha@gmail.com'),
        'phone_no': openapi.Schema(type=openapi.TYPE_STRING, example='9876543210'),
        'address': openapi.Schema(type=openapi.TYPE_STRING, example='Pune'),
        'city': openapi.Schema(type=openapi.TYPE_STRING, example='Pune'),
        'state': openapi.Schema(type=openapi.TYPE_STRING, example='Maharashtra'),
        'pincode': openapi.Schema(type=openapi.TYPE_STRING, example='411001'),
        'role': openapi.Schema(type=openapi.TYPE_STRING, example='SUPERADMIN'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, example='diksha123')
    }
)

login_example = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, example='diksha'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, example='diksha123')
    }
)

# ✅ Registration
class RegisterView(APIView):
    permission_classes = [AllowAny] 
    @swagger_auto_schema(request_body=registration_example)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_no": user.phone_no,
                    "address": user.address,
                    "city": user.city,
                    "state": user.state,
                    "pincode": user.pincode,
                    "role": user.role.name if user.role else None,
                    
                    
                },
                "tokens": {
                    
                    "access": str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# ✅ Login
class LoginView(APIView):
    permission_classes = [AllowAny] 
    @swagger_auto_schema(request_body=login_example)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone_no": user.phone_no,
                        "address": user.address,
                        "city": user.city,
                        "state": user.state,
                        "image": request.build_absolute_uri(user.image.url) if user.image else None,
                        "pincode": user.pincode,
                        "role": user.role.name if user.role else None,
                      
                       
                    },
                    "tokens": {
                       
                        "access": str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK)
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": "Login failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
