from rest_framework import serializers
from .models import CustomUser
#FarmerProfile, InvestorProfile
from .models import LoginLog
from .models import Project,ProjectUpdate,KYCUpload,Transaction
import cloudinary.uploader
import requests
from django.core.files.base import ContentFile
# -----------------------------
# CustomUser serializer -> for getting user info
# -----------------------------
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


# -----------------------------
# Registration serializer -> Creating new user
# -----------------------------

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email','first_name', 'last_name','role','password','hedera_private_key','hedera_account_id']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Create user using manager to ensure password hashing
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


# -----------------------------
# Registration serializer -> admin login logs
# -----------------------------


class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginLog
        fields = ['id', 'user', 'email', 'success', 'ip_address', 'user_agent', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

# -----------------------------
# Project Serializer -> framer's project POST|GET|DELETE|PUT|PATCH
# -----------------------------

class ProjectSerializer(serializers.ModelSerializer):
    percent_funded = serializers.IntegerField(read_only=True)
    farmer_email = serializers.CharField(source='farmer.email', read_only=True)
    farmer_first_name = serializers.CharField(source='farmer.first_name', read_only=True) 
    farmer_hedera_account_id= serializers.CharField(source='farmer.hedera_account_id', read_only=True)
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False)
    image_link = serializers.URLField(write_only=True, required=False)
    class Meta:
        model = Project
        fields = ['id', 'title', 'short_description', 'description', 'location','farmer_first_name','farmer_hedera_account_id', 'funding_goal', 'funds_raised', 'investors_count', 'status', 'image', 'image_link', 'image_url', 'is_public', 'created_at', 'updated_at', 'percent_funded', 'farmer', 'farmer_email']
        read_only_fields = ['id', 'created_at', 'updated_at', 'percent_funded', 'farmer_email','farmer_first_name', 'farmer','farmer_hedera_account_id']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        image_link = validated_data.pop('image_link', None)

        if image:
            validated_data['image'] = image
        elif image_link:
            response = requests.get(image_link)
            if response.status_code == 200:
                file_name = image_link.split("/")[-1]
                uploaded = cloudinary.uploader.upload(ContentFile(response.content, name=file_name))
                validated_data['image'] = uploaded['public_id']

        return super().create(validated_data)
# -----------------------------
# ProjectUpdate Serializer -> update above project 
# -----------------------------
class ProjectUpdateSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    class Meta:
        model = Project
        fields = ['id']


# -----------------------------
# ProjectUpdateCreateSerializern 
# -----------------------------
class ProjectUpdateCreateSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    class Meta:
        model = ProjectUpdate
        fields = ['id', 'project', 'author', 'content', 'image', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


# -----------------------------
# CustomUser Registration 
# -----------------------------
class KYCUploadSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = KYCUpload
        fields = ['id', 'user', 'document', 'status', 'submitted_at', 'user_email']
        read_only_fields = ['id', 'status', 'submitted_at', 'user']


# -----------------------------
# CustmUser Registration 
# -----------------------------
# transactions/serializers.py
from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    sender_email = serializers.EmailField(source="sender.email", read_only=True)
    receiver_email = serializers.EmailField(source="receiver.email", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "project",
            "project_title",
            "sender",
            "sender_email",
            "receiver",
            "receiver_email",
            "tx_type",
            "amount_hbar",
            "hedera_tx_id",
            "status",
            "created_at",
            "completed_at",
            "notes",
        ]
        read_only_fields = [
            "id",
            
            "created_at",
            "completed_at",
            "sender_email",
            "receiver_email",
            "project_title",
        ]
