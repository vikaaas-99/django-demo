from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


# Serializer for user signup
class SignUpSerializer(serializers.Serializer):
    """
    Serializer for user signup.

    Fields:
        - username: A string representing the user's desired username.
        - password: A string representing the user's desired password.
    """

    username = serializers.CharField(min_length=5, max_length=15, required=True)
    password = serializers.CharField(min_length=5, max_length=15, required=True)

    def validate(self, data):
        """
        Validate the provided data.

        Checks if the username already exists.

        Raises:
            - ValidationError: If the username already exists.
        """
        username = data["username"]
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
        return data
    
    def signup_user(self, validated_data):
        """
        Create a new user with the validated data.

        Returns:
            - The username of the newly created user.
        """
        username = validated_data["username"]
        password = validated_data["password"]

        user = User.objects.create_user(username=username, password=password)
        return user.username
    

# Serializer for user login
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Fields:
        - username: A string representing the user's username.
        - password: A string representing the user's password.
    """
            
    username = serializers.CharField(min_length=5, max_length=15, required=True)
    password = serializers.CharField(min_length=5, max_length=15, required=True)
    
    def validate(self, data):
        """
        Validate the provided data.

        Checks if the username exists and if the password is correct.

        Raises:
            - ValidationError: If the username does not exist or the password is incorrect.
        """
        username = data["username"]
        password = data["password"]
        
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username does not exist")
        
        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password")
        return data
        
    def login_user(self, validated_data):
        """
        Generate a JWT token for the validated user.

        Returns:
            - A dictionary containing the access token.
        """
        username = validated_data["username"]

        user = User.objects.get(username=username)

        # Generate token
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token)}