from django.contrib import admin
from .models import Category, UserProfile, Auction, Bid


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['icon', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'auctions_created', 'auctions_won', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display   = ['title', 'seller', 'category', 'status',
                      'base_price', 'current_price', 'closing_date']
    list_filter    = ['status', 'category']
    search_fields  = ['title', 'seller__username']
    readonly_fields = ['created_at', 'current_price', 'winner']
    date_hierarchy = 'closing_date'


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display  = ['bidder', 'auction', 'amount', 'created_at']
    list_filter   = ['auction__status']
    search_fields = ['bidder__username', 'auction__title']
    readonly_fields = ['created_at']
