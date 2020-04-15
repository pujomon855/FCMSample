from django.contrib import admin

from .models import Client, Code, CodeSession, CodeSessionProduct, HandlInst, Product, Session, SessionProduct


admin.site.register(Client)
admin.site.register(Code)
admin.site.register(CodeSession)
admin.site.register(CodeSessionProduct)
admin.site.register(HandlInst)
admin.site.register(Product)
admin.site.register(Session)
admin.site.register(SessionProduct)
