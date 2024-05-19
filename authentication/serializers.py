from django.contrib.auth import password_validation
from authentication.models import CustomUser as User
from rest_framework import serializers

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")

        password_validation.validate_password(data['password'], self.instance)
        self.validate_names(data['first_name'], data['last_name'])

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

    def validate_names(self, first_name, last_name):
        if not first_name.strip().isalpha():
            raise serializers.ValidationError("First name must contain only letters.")
        if not last_name.strip().isalpha():
            raise serializers.ValidationError("Last name must contain only letters.")
