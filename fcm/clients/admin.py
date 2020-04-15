from django.contrib import admin

from .models import Client, Code, CodeSession, CodeSessionProduct, HandlInst, Product, Session, SessionProduct


class CodeInLine(admin.StackedInline):
    model = Code


class ClientAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'client_id']}),
    ]
    inlines = [CodeInLine]


admin.site.register(Client, ClientAdmin)


class CodeSessionInLine(admin.TabularInline):
    model = CodeSession


class SessionProductInLine(admin.TabularInline):
    model = SessionProduct


class CodeSessionProductInLine(admin.TabularInline):
    model = CodeSessionProduct


class SessionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Time information', {'fields': ['start_time', 'end_time']}),
    ]
    inlines = [CodeSessionInLine, SessionProductInLine, CodeSessionProductInLine]


admin.site.register(Session, SessionAdmin)

admin.site.register(HandlInst)
admin.site.register(Product)
