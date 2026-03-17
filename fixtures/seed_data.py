import os
import django
import sys
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from apps.auctions.models import Category, Auction, Bid

# ── Usuarios ──────────────────────────────────
print('Creando usuarios...')
mariana, _ = User.objects.get_or_create(username='mariana', defaults={'email': 'mariana@test.cl'})
mariana.set_password('test1234')
mariana.save()

carlos, _ = User.objects.get_or_create(username='carlos', defaults={'email': 'carlos@test.cl'})
carlos.set_password('test1234')
carlos.save()

print('  ✓ mariana / test1234')
print('  ✓ carlos  / test1234')

# ── Categorías (ya deben existir) ─────────────
relojes    = Category.objects.get(slug='relojes')
vinilos    = Category.objects.get(slug='vinilos-y-musica')
joyeria    = Category.objects.get(slug='joyeria')
muebles    = Category.objects.get(slug='muebles')

# ── Subastas ──────────────────────────────────
print('\nCreando subastas...')
now = timezone.now()

a1, _ = Auction.objects.get_or_create(
    title='Gramófono Columbia 1920',
    defaults={
        'description': 'Gramófono original Columbia en excelente estado. Funciona perfectamente.',
        'base_price': 85000,
        'current_price': 85000,
        'closing_date': now + timedelta(hours=2),
        'status': 'active',
        'seller': mariana,
        'category': relojes,
    }
)

a2, _ = Auction.objects.get_or_create(
    title='Reloj de bolsillo Longines 1935',
    defaults={
        'description': 'Reloj de bolsillo suizo, caja de plata, mecanismo original.',
        'base_price': 120000,
        'current_price': 120000,
        'closing_date': now + timedelta(days=2),
        'status': 'active',
        'seller': carlos,
        'category': relojes,
    }
)

a3, _ = Auction.objects.get_or_create(
    title='Vinilo original The Beatles - Abbey Road 1969',
    defaults={
        'description': 'Primera edición chilena. Excelente estado, sin rayones.',
        'base_price': 45000,
        'current_price': 45000,
        'closing_date': now + timedelta(days=5),
        'status': 'active',
        'seller': mariana,
        'category': vinilos,
    }
)

a4, _ = Auction.objects.get_or_create(
    title='Anillo victoriano con piedra granate',
    defaults={
        'description': 'Anillo de oro 18k época victoriana, piedra granate central.',
        'base_price': 200000,
        'current_price': 200000,
        'closing_date': now + timedelta(days=3),
        'status': 'active',
        'seller': carlos,
        'category': joyeria,
    }
)

print('  ✓ 4 subastas activas creadas')

# ── Ofertas ───────────────────────────────────
print('\nCreando ofertas...')

if not Bid.objects.filter(auction=a1).exists():
    Bid.objects.create(auction=a1, bidder=carlos,  amount=90000)
    Bid.objects.create(auction=a1, bidder=mariana, amount=105000)
    Bid.objects.create(auction=a1, bidder=carlos,  amount=120000)
    a1.current_price = 120000
    a1.save(update_fields=['current_price'])

if not Bid.objects.filter(auction=a2).exists():
    Bid.objects.create(auction=a2, bidder=mariana, amount=135000)
    a2.current_price = 135000
    a2.save(update_fields=['current_price'])

print('  ✓ Ofertas registradas')
print('\n✅ Seed completado. Visita http://127.0.0.1:8000')
