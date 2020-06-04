from django.contrib import admin

from .models import Client, ClientClassifier, CodeSession, TradeType, HandlInst, Product, Session
from .models import Currency, CostType, ChangeType, Vendor, Cost


class ClientClassifierInline(admin.StackedInline):
    model = ClientClassifier
    fieldsets = [
        (None, {'fields': (('identifier', 'view', 'code'),)}),
    ]
    extra = 1
    template = 'admin/clients/client_classifier/edit_inline/stacked.html'


class ClientAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
    ]
    inlines = [ClientClassifierInline]
    search_fields = ['name']
    ordering = ['name']


admin.site.register(Client, ClientAdmin)


class CodeSessionInLine(admin.TabularInline):
    model = CodeSession


class TradeTypeInLine(admin.TabularInline):
    model = TradeType


class SessionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Time information', {'fields': ['start_time', 'end_time']}),
    ]
    inlines = [CodeSessionInLine, TradeTypeInLine]
    search_fields = ['name']


admin.site.register(Session, SessionAdmin)

admin.site.register(HandlInst)
admin.site.register(Product)
admin.site.register(CostType)
admin.site.register(ChangeType)
admin.site.register(Vendor)
admin.site.register(Cost)
admin.site.register(Currency)
