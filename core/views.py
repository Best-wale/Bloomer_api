from rest_framework import generics, permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from .models import Project,Transaction,LoginLog
from .serializers import ProjectSerializer, LoginLogSerializer,TransactionSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.db.models import Q


from decimal import Decimal
from django.db import transaction as db_transaction

class ProjectListCreateView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        #For authenciated !user
        if not user.is_authenticated:
            return Project.objects.filter(is_public=True)


        #For authenciated user
        return Project.objects.filter( Q(farmer=user)).distinct()

    def perform_create(self,serializer):
        serializer.save(farmer=self.request.user)







class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # allow public read without auth if project.is_public
        obj = self.get_object()
        if obj.is_public:
            self.permission_classes = [AllowAny]
        return super().get(request, *args, **kwargs)


from .models import CustomUser
#FarmerProfile, InvestorProfile
from .serializers import (
    CustomUserSerializer, RegisterSerializer,
    #FarmerProfileSerializer, InvestorProfileSerializer
)
from .serializers import ProjectUpdateCreateSerializer, KYCUploadSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
import secrets


# -----------------------------
# CustomUser Registration
# -----------------------------
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # Use serializer to create user (which will set password via serializer.create)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Create auth token for the new user
        token, _ = Token.objects.get_or_create(user=user)
        data = CustomUserSerializer(user).data
        return Response({'token': token.key, 'user': data}, status=status.HTTP_201_CREATED)


# -----------------------------
# Current CustomUser
# -----------------------------
class MeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        ip = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR')
        ua = request.META.get('HTTP_USER_AGENT', '')

        user = None
        success = False
        message = ''

        if not email or not password:
            message = 'Email and password are required.'
            LoginLog.objects.create(email=email, success=False, ip_address=ip, user_agent=ua, message=message)
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        if user is None:
            message = 'Invalid credentials.'
            LoginLog.objects.create(email=email, success=False, ip_address=ip, user_agent=ua, message=message)
            return Response({'error': message}, status=status.HTTP_401_UNAUTHORIZED)

        # At this point authentication succeeded
        success = True
        # create or get token
        token, created = Token.objects.get_or_create(user=user)

        LoginLog.objects.create(user=user, email=email, success=True, ip_address=ip, user_agent=ua, message='Login successful')
        print(CustomUserSerializer(user).data)
        return Response({'token': token.key, 'user': CustomUserSerializer(user).data})


# Endpoint: POST /bloomr/projects/<pk>/updates/  (create update for a project)
class ProjectUpdateCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectUpdateCreateSerializer

    def perform_create(self, serializer):
        # Ensure author is the authenticated user and project exists
        user = self.request.user
        project = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        # Only the farmer who owns the project may post updates
        if project.farmer != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the project owner may post updates')
        serializer.save(author=user, project=project)


# Endpoint: POST /bloomr/kyc/  (file upload)
class KYCUploadCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = KYCUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WalletConnectView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet = request.data.get('wallet_address')
        if not wallet:
            return Response({'detail': 'wallet_address required'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.wallet_address = wallet
        user.save()
        return Response({'detail': 'wallet saved', 'wallet_address': wallet})


class WalletNonceView(APIView):
    """GET: create a nonce for the authenticated user.
       POST: optionally accept wallet_address to create nonce for different address.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        nonce = secrets.token_hex(16)
        from .models import WalletNonce
        wn = WalletNonce.objects.create(user=user, nonce=nonce)
        return Response({'nonce': nonce, 'id': wn.id})


class WalletVerifyView(APIView):
    """Accepts { wallet_address, nonce, signature } and verifies ownership.
       NOTE: This is a placeholder that marks verification as successful; for production
       you must verify the signature using Hedera SDK or HashConnect client signed payloads.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet = request.data.get('wallet_address')
        nonce = request.data.get('nonce')
        signature = request.data.get('signature')
        if not wallet or not nonce or not signature:
            return Response({'detail': 'wallet_address, nonce and signature required'}, status=status.HTTP_400_BAD_REQUEST)
        from .models import WalletNonce
        try:
            wn = WalletNonce.objects.get(nonce=nonce, user=request.user, used=False)
        except WalletNonce.DoesNotExist:
            return Response({'detail': 'Invalid or used nonce'}, status=status.HTTP_400_BAD_REQUEST)

        # Placeholder verification: in production, verify `signature` properly here.
        # For now, accept any signature and mark nonce used.
        wn.used = True
        wn.save()
        user = request.user
        user.wallet_address = wallet
        user.save()
        return Response({'detail': 'wallet verified and bound', 'wallet_address': wallet})


# -----------------------------
# Farmer Profile (view/update)
# -----------------------------




class TransactionViewSet(viewsets.ModelViewSet):
    """
    /api/transactions/
    Supports GET (list/detail) and POST for creating a transaction.
    """
    queryset = Transaction.objects.select_related("project", "sender", "receiver").all()
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def perform_create(self, serializer):
        # Auto-set sender to current user if not explicitly provided
        transaction_obj = serializer.save(sender=self.request.user)

        #update project funds_raised 
        project = transaction_obj.project
        project.funds_raised = (project.funds_raised or Decimal('0')) +transaction_obj.amount_hbar

        unique_investors = (
            Transaction.objects
            .filter(project=project)
            .values("sender")
            .distinct()
            .count()
        )
        project.investors_count = unique_investors
        print(unique_investors)
        project.save(update_fields=["funds_raised","investors_count"]) 