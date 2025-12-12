from django.urls import path
from .views import (LoginView,
                    LogoutView,
                    MeView,
                    SignupView,
                    ClearTokenView,
                    CSRFCookieView,
                    UserProfileMeView,
                    RegisterStudentByTeacherView,
                    RegisterView,
                    AccountsListView,
                    AccountDetailView,
                    DeactivateAccountsView,
                    ReactivateAccountsView,
                    DeleteAccountsView,
                    DeletedAccountListView
                    
                    
                    )

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('clear-tokens/', ClearTokenView.as_view(), name='clear-tokens'),
    path('csrf/', CSRFCookieView.as_view(), name='csrf'),
    path('me/', MeView.as_view(), name='me'),
    path("profile/me/", UserProfileMeView.as_view()),
    # path("register/", RegisterStudentByTeacherView.as_view()),
    path("register/", RegisterView.as_view()),
    path("account/list/",AccountsListView.as_view()),
    path("account/<uuid:user_id>/detail/",AccountDetailView.as_view()),
    path("account/<uuid:user_id>/deactivate/", DeactivateAccountsView.as_view()),
    path("account/<uuid:user_id>/reactivate/", ReactivateAccountsView.as_view()),
    path("account/<uuid:user_id>/delete/", DeleteAccountsView.as_view()),
    path("account/deleted/logs/", DeletedAccountListView.as_view()),



]