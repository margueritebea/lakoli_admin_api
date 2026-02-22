"""
URLs pour l'app authentication.
À inclure dans le urls.py principal :
  path('api/auth/', include('apps.authentication.urls')),
"""
from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    MeView,
    ChangePasswordView,
    ResetPasswordRequestView,
    ResetPasswordConfirmView,
    UserListCreateView,
    UserDetailView,
)

app_name = 'authentication'

urlpatterns = [
    # ── Session ──────────────────────────────────────────────────────────────
    path('login/',                      LoginView.as_view(),              name='login'),
    path('logout/',                     LogoutView.as_view(),             name='logout'),
    path('refresh/',                    RefreshTokenView.as_view(),       name='token-refresh'),

    # ── Profil personnel ─────────────────────────────────────────────────────
    path('me/',                         MeView.as_view(),                 name='me'),
    path('change-password/',            ChangePasswordView.as_view(),     name='change-password'),

    # ── Réinitialisation mot de passe ────────────────────────────────────────
    path('reset-password/',             ResetPasswordRequestView.as_view(), name='reset-password'),
    path('reset-password/confirm/',     ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),

    # ── Gestionutilisateurs (admin) ─────────────────────────────────────────
    path('',                            UserListCreateView.as_view(),     name='user-list'),
    path('<int:pk>/',                  UserDetailView.as_view(),         name='user-detail'),
]