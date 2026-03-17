from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


# ─────────────────────────────────────────
# CATEGORÍA
# Sustantivo de HU-06
# ─────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, default='🏺')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


# ─────────────────────────────────────────
# PERFIL DE USUARIO
# Sustantivo de HU-01
# ─────────────────────────────────────────
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )
    auctions_created = models.PositiveIntegerField(default=0)
    auctions_won = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'Perfil de {self.user.username}'


# ─────────────────────────────────────────
# SUBASTA
# Sustantivo central de HU-02, HU-04, HU-07
# ─────────────────────────────────────────
class Auction(models.Model):

    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Activa'
        CLOSED   = 'closed',   'Cerrada'
        DESERTED = 'deserted', 'Desierta'

    title         = models.CharField(max_length=200)
    description   = models.TextField()
    image         = models.ImageField(upload_to='auctions/')
    base_price    = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    closing_date  = models.DateTimeField()
    status        = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    seller        = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auctions'
    )
    category      = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='auctions'
    )
    winner        = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auctions_won'
    )
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Subasta'
        verbose_name_plural = 'Subastas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['closing_date']),
        ]

    def __str__(self):
        return self.title

    # Verbo de HU-02: "no permitir fecha de cierre en el pasado"
    def clean(self):
        if self.closing_date and self.closing_date <= timezone.now():
            raise ValidationError(
                {'closing_date': 'La fecha de cierre debe ser en el futuro.'}
            )

    # QuerySet helper: precio mínimo para la siguiente oferta
    def minimum_bid(self):
        if self.current_price:
            return self.current_price + 1
        return self.base_price

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


# ─────────────────────────────────────────
# OFERTA
# Sustantivo de HU-03, HU-05
# ─────────────────────────────────────────
class Bid(models.Model):
    auction    = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    bidder     = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.bidder.username} — ${self.amount} en {self.auction.title}'

    # Verbos de HU-03: validar todas las reglas de negocio
    def clean(self):
        # Regla 1: solo subastas activas
        if self.auction.status != Auction.Status.ACTIVE:
            raise ValidationError('Esta subasta ya no está activa.')

        # Regla 2: el vendedor no puede ofertar en su propia subasta
        if self.bidder == self.auction.seller:
            raise ValidationError('No puedes ofertar en tu propia subasta.')

        # Regla 3: monto mínimo
        if self.auction.current_price:
            if self.amount <= self.auction.current_price:
                raise ValidationError(
                    f'Tu oferta debe ser mayor a ${self.auction.current_price}.'
                )
        else:
            if self.amount < self.auction.base_price:
                raise ValidationError(
                    f'Tu oferta debe ser igual o mayor al precio base (${self.auction.base_price}).'
                )
