# -*- coding: utf-8 -*-

from django.forms import Form, ModelForm, BooleanField, ModelChoiceField

from .models import Client, ClientClassifier, CodeSession, TradeType, HandlInst, Product, Session


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = [
            'name',
        ]


class ViewCodeForm(ModelForm):
    class Meta:
        model = ClientClassifier
        fields = [
            'identifier',
            'view',
            'code',
        ]


class ViewCodeSessionForm(ModelForm):
    session = ModelChoiceField(Session.objects.all())
    eq_disc = BooleanField(required=False)
    eq_dma = BooleanField(required=False)
    eq_dsa = BooleanField(required=False)
    fu_disc = BooleanField(required=False)
    fu_dma = BooleanField(required=False)
    fu_dsa = BooleanField(required=False)
    op_disc = BooleanField(required=False)
    op_dma = BooleanField(required=False)
    op_dsa = BooleanField(required=False)
    sp_disc = BooleanField(required=False)
    sp_dma = BooleanField(required=False)
    sp_dsa = BooleanField(required=False)

    class Meta:
        model = CodeSession
        fields = [
            'connection_start_date',
            'connection_end_date',
        ]
