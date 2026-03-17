from django.urls import path
from . import views

urlpatterns = [
    # HU-08: Página principal
    path('', views.HomeView.as_view(), name='home'),

    # HU-01: Registro
    path('registro/', views.RegisterView.as_view(), name='register'),

    # HU-01: Perfil público
    path('perfil/<str:username>/', views.ProfileView.as_view(), name='profile'),

    # HU-02: Crear subasta
    path('subastas/crear/', views.AuctionCreateView.as_view(), name='auction_create'),

    # HU-05: Detalle + historial de ofertas
    path('subastas/<int:pk>/', views.AuctionDetailView.as_view(), name='auction_detail'),

    # HU-03: Realizar oferta
    path('subastas/<int:pk>/ofertar/', views.PlaceBidView.as_view(), name='place_bid'),

    # HU-07: Panel del vendedor
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
