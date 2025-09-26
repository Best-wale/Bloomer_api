from django.urls import path,include
from .views import RegisterView, MeView, LoginAPIView
from .views import ProjectListCreateView, ProjectDetailView
from .views import ProjectUpdateCreateView, KYCUploadCreateView,TransactionViewSet
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r'transactions', TransactionViewSet,basename='transactions')
router.register(r'project',ProjectListCreateView,basename='projects')

urlpatterns = [
    #Authentication of all users
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),  # custom token login with logging
    path('me/', MeView.as_view(), name='me'),

    path('kyc/', KYCUploadCreateView.as_view(), name='kyc-upload'),
    # transactions Get and Post url
    path('', include(router.urls)),
   
]
#    path('farmer/profile/', FarmerProfileView.as_view(), name='farmer_profile'),
#   path('investor/profile/', InvestorProfileView.as_view(), name='investor_profile'),

'''
    path('projects/', ProjectListCreateView.as_view(), name='projects'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/updates/', ProjectUpdateCreateView.as_view(), name='project-updates'),
'''