from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from cloudinary.models import CloudinaryField
import cloudinary.uploader
# ---------------------------------------------------------------------
# 1. Custom User
# ---------------------------------------------------------------------





class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('investor', 'Investor'),
        ('farmer', 'Farmer'),
        
    ]
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='investor',
        help_text="Determines user capabilities in the system.")
    hedera_account_id = models.CharField(max_length=200, blank=True, null=True, help_text='Optional Hedera account id ')
    hedera_private_key = models.TextField(blank=True,null=True)
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS should list the names of required fields (strings),
    # not the field objects. Include fields that should be prompted when
    # creating a superuser (email is the USERNAME_FIELD so exclude it).
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ---------------------------------------------------------------------
# 5. Login Audit Log
# ---------------------------------------------------------------------
class LoginLog(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='login_logs')
    email = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"LoginLog(email={self.email} success={self.success} at={self.created_at})"


# ---------------------------------------------------------------------
# 6. Farm Project (detailed)
# ---------------------------------------------------------------------
class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('fundraising', 'Fundraising'),
        ('growing', 'Growing'),
        ('harvest', 'Harvest Phase'),
        ('completed', 'Completed'),
        ('closed', 'Closed')
    ]

    farmer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects', limit_choices_to={'role': 'farmer'})
    title = models.CharField(max_length=150)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    funding_goal = models.DecimalField(max_digits=12, decimal_places=2)
    funds_raised = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    investors_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    image = CloudinaryField('image',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.farmer.email})"

    @property
    def percent_funded(self):
        try:
            if not self.funding_goal or self.funding_goal == 0:
                return 0
            return min(100, int((self.funds_raised / self.funding_goal) * 100))
        except Exception:
            return 0


# ---------------------------------------------------------------------
# 7. Project Updates
# ---------------------------------------------------------------------
class ProjectUpdate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_updates')
    content = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True, help_text='Optional image or emoji id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update for {self.project.title} by {self.author.email} at {self.created_at}"


# ---------------------------------------------------------------------
# 8. KYC Uploads
# ---------------------------------------------------------------------
class KYCUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='kyc_uploads')
    document = models.FileField(upload_to='kyc_documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KYC {self.user.email} - {self.status}"


# ---------------------------------------------------------------------
# 9. Wallet Nonce for verification
# ---------------------------------------------------------------------
#class Investment(mdoe)



# ---------------------------------------------------------------------
# 9. Wallet Nonce for verification
# ---------------------------------------------------------------------

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Transaction(models.Model):
    TYPE_CHOICES = [
        ("investment", "Investment"),   # Investor → Escrow
        ("disbursement", "Disbursement"), # Escrow → Farmer
        ("repayment", "Repayment"),     # Farmer → Investor(s)
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="transactions")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions_sent")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions_received")

    tx_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    amount_hbar = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0.0"))

    hedera_tx_id = models.CharField(max_length=255, null=True, blank=True, help_text="Hedera transaction hash/ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    def mark_success(self, tx_id: str):
        self.status = "success"
        self.hedra_tx_id = tx_id
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, reason: str = None):
        self.status = "failed"
        self.notes = (self.notes or "") + f"\nFailed: {reason}"
        self.completed_at = timezone.now()
        self.save()

    def _str_(self):
        return f"{self.tx_type} | {self.amount_ngn} NGN ({self.status})"


