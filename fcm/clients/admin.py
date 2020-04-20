from django.contrib import admin

from .models import Client, ClientClassifier, CodeSession, TradeType, HandlInst, Product, Session


class ClientClassifierInLine(admin.StackedInline):
    model = ClientClassifier
    fieldsets = [
        (None, {'fields': (('identifier', 'view', 'code'),)}),
    ]
    extra = 1
    template = 'admin/clients/clientclassifier/edit_inline/stacked.html'


class ClientAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
    ]
    inlines = [ClientClassifierInLine]
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
