# users/serializers/user_serializers.py
from rest_framework import serializers
from users.models import User, UserRole
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Enter your password"
    )
    role = serializers.CharField(
        write_only=True, required=True,
        help_text="Enter role name (case-insensitive, e.g., 'Admin')"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_no', 'address', 'city', 'state', 'pincode', 'role', 'password', 'image']
        extra_kwargs = {
            'username': {'required': True, 'help_text': 'Enter username'},
            'email': {'required': True, 'help_text': 'Enter email'},
            'first_name': {'required': True, 'help_text': 'Enter first name'},
            'last_name': {'required': True, 'help_text': 'Enter last name'},
        }

    # Duplicate checks
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_phone_no(self, value):
        if User.objects.filter(phone_no=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        role_name = validated_data.pop('role')

        try:
            role_obj = UserRole.objects.get(name__iexact=role_name)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError({"role": f"Role '{role_name}' not found"})

        # SuperAdmin flags
        if role_obj.name.lower() == 'superadmin':
            validated_data['is_superuser'] = True
            validated_data['is_staff'] = True
        else:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False

        user = User.objects.create(role=role_obj, **validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Enter username")
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
