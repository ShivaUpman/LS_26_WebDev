from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Bounty

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password')

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A citizen with this name already resides in this town.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class BountySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Bounty
        fields = ('id', 'target_name', 'reward', 'status', 'owner', 'danger_level', 'last_seen_at', 'created_at', 'updated_at')

    def validate_status(self, value):
        valid_statuses = ['wanted', 'captured']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be either 'wanted' or 'captured'. Received: {value}")
        return value

    def validate_reward(self, value):
        if value <= 0:
            raise serializers.ValidationError("A bounty reward must be greater than zero! No bounty hunter works for free.")
        return value
