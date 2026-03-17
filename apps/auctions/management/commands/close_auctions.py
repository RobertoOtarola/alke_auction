from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.auctions.models import Auction, Bid


class Command(BaseCommand):
    help = 'Cierra las subastas expiradas y determina al ganador.'

    def handle(self, *args, **kwargs):
        expiradas = Auction.objects.filter(
            status=Auction.Status.ACTIVE,
            closing_date__lte=timezone.now()
        )

        total = expiradas.count()
        cerradas = 0
        desiertas = 0

        for auction in expiradas:
            oferta_ganadora = Bid.objects.filter(
                auction=auction
            ).order_by('-amount').first()

            if oferta_ganadora:
                auction.status = Auction.Status.CLOSED
                auction.winner = oferta_ganadora.bidder
                auction.current_price = oferta_ganadora.amount
                cerradas += 1
            else:
                auction.status = Auction.Status.DESERTED
                desiertas += 1

            auction.save(update_fields=['status', 'winner', 'current_price'])
            self.stdout.write(f'  {"✓" if oferta_ganadora else "○"} {auction.title} → {auction.get_status_display()}')

        self.stdout.write(self.style.SUCCESS(
            f'\nListo: {total} procesadas — {cerradas} cerradas, {desiertas} desiertas.'
        ))
