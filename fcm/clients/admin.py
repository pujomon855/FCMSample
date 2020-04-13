from django.contrib import admin

from .models import Client, Code, CodeSessionLogic, CodeSessionProduct, Product, Session, SessionProduct


admin.site.register(Client)
admin.site.register(Code)
admin.site.register(CodeSessionLogic)
admin.site.register(CodeSessionProduct)
admin.site.register(Product)
admin.site.register(Session)
admin.site.register(SessionProduct)
