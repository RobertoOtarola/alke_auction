from django.views.generic import View, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from .models import Auction, Bid, Category
from .forms import RegisterForm, AuctionForm, BidForm


# ─────────────────────────────────────────
# HU-08: Página principal
# ─────────────────────────────────────────
class HomeView(View):
    def get(self, request):
        categorias = Category.objects.all()
        categoria_slug = request.GET.get('categoria')
        q = request.GET.get('q', '').strip()

        subastas = Auction.objects.filter(
            status=Auction.Status.ACTIVE
        ).select_related('category', 'seller')

        if categoria_slug:
            subastas = subastas.filter(category__slug=categoria_slug)

        if q:
            subastas = subastas.filter(title__icontains=q)

        por_cerrar = subastas.order_by('closing_date')[:6]
        mas_ofertas = subastas.annotate(
            bid_count=Count('bids')
        ).order_by('-bid_count')[:6]
        recientes = subastas.order_by('-created_at')[:6]

        return render(request, 'auctions/home.html', {
            'categorias': categorias,
            'por_cerrar': por_cerrar,
            'mas_ofertas': mas_ofertas,
            'recientes': recientes,
            'q': q,
            'categoria_activa': categoria_slug,
        })


# ─────────────────────────────────────────
# HU-01: Registro
# ─────────────────────────────────────────
class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            return redirect('home')
        return render(request, 'registration/register.html', {'form': form})


# ─────────────────────────────────────────
# HU-01 / HU-05: Perfil público
# ─────────────────────────────────────────
class ProfileView(View):
    def get(self, request, username):
        usuario = get_object_or_404(User, username=username)
        subastas_creadas = Auction.objects.filter(
            seller=usuario
        ).order_by('-created_at')
        subastas_ganadas = Auction.objects.filter(
            winner=usuario
        ).order_by('-created_at')
        ofertas = Bid.objects.filter(
            bidder=usuario
        ).select_related('auction').order_by('-created_at')

        return render(request, 'auctions/profile.html', {
            'perfil_usuario': usuario,
            'subastas_creadas': subastas_creadas,
            'subastas_ganadas': subastas_ganadas,
            'ofertas': ofertas,
        })


# ─────────────────────────────────────────
# HU-02: Crear subasta
# ─────────────────────────────────────────
class AuctionCreateView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request):
        form = AuctionForm()
        return render(request, 'auctions/auction_create.html', {'form': form})

    def post(self, request):
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            auction.current_price = auction.base_price
            auction.full_clean()
            auction.save()
            messages.success(request, '¡Subasta publicada exitosamente!')
            return redirect('auction_detail', pk=auction.pk)
        return render(request, 'auctions/auction_create.html', {'form': form})


# ─────────────────────────────────────────
# HU-03 / HU-05: Detalle e historial
# ─────────────────────────────────────────
class AuctionDetailView(View):
    def get(self, request, pk):
        auction = get_object_or_404(
            Auction.objects.select_related('seller', 'category', 'winner'),
            pk=pk
        )
        bids = auction.bids.select_related('bidder').order_by('-created_at')
        form = BidForm()

        return render(request, 'auctions/auction_detail.html', {
            'auction': auction,
            'bids': bids,
            'form': form,
        })


# ─────────────────────────────────────────
# HU-03: Realizar oferta
# ─────────────────────────────────────────
class PlaceBidView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def post(self, request, pk):
        auction = get_object_or_404(Auction, pk=pk)

        # Validación 1: subasta activa
        if not auction.is_active:
            messages.error(request, 'Esta subasta ya no está activa.')
            return redirect('auction_detail', pk=pk)

        # Validación 2: vendedor no puede ofertar
        if request.user == auction.seller:
            messages.error(request, 'No puedes ofertar en tu propia subasta.')
            return redirect('auction_detail', pk=pk)

        form = BidForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    auction = Auction.objects.select_for_update().get(pk=pk)
                    bid = form.save(commit=False)
                    bid.auction = auction
                    bid.bidder = request.user
                    bid.full_clean()
                    bid.save()

                    # Actualizar precio desnormalizado
                    auction.current_price = bid.amount
                    auction.save(update_fields=['current_price'])

                messages.success(
                    request, f'¡Oferta de ${bid.amount} registrada!'
                )
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Monto inválido.')

        return redirect('auction_detail', pk=pk)


# ─────────────────────────────────────────
# HU-07: Panel del vendedor
# ─────────────────────────────────────────
class DashboardView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request):
        mis_subastas = Auction.objects.filter(
            seller=request.user
        ).prefetch_related('bids').order_by('-created_at')

        activas  = mis_subastas.filter(status=Auction.Status.ACTIVE)
        cerradas = mis_subastas.filter(status=Auction.Status.CLOSED)
        desiertas = mis_subastas.filter(status=Auction.Status.DESERTED)

        total = mis_subastas.count()
        exitosas = cerradas.count()
        porcentaje = round((exitosas / total * 100), 1) if total > 0 else 0

        return render(request, 'auctions/dashboard.html', {
            'activas': activas,
            'cerradas': cerradas,
            'desiertas': desiertas,
            'total': total,
            'exitosas': exitosas,
            'porcentaje': porcentaje,
        })
