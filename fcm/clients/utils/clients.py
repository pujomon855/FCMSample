# -*- coding: utf-8 -*-

from ..models import Product, HandlInst


__PRODUCT_DICT = {
    'eq': Product.objects.get(name='Equity'),
    'fu': Product.objects.get(name='Future'),
    'op': Product.objects.get(name='Option'),
    'sp': Product.objects.get(name='Spread'),
}

__HANDLINST_DICT = {
    'disc': HandlInst.objects.get(name='DISC'),
    'dma': HandlInst.objects.get(name='DMA'),
    'dsa': HandlInst.objects.get(name='DSA'),
}


def get_product(key):
    product = __PRODUCT_DICT.get(key)
    if product:
        return product
    return Product.objects.get(name=key)


def get_handlinst(key):
    handlinst = __HANDLINST_DICT.get(key)
    if handlinst:
        return handlinst
    return HandlInst.objects.get(name=key)


def trade_types_sdb_to_str(trade_types_sdb):
    trade_types = []
    if trade_types_sdb.eq_disc:
        trade_types.append('CD')
    if trade_types_sdb.eq_dma:
        trade_types.append('DMA')
    if trade_types_sdb.eq_dsa:
        trade_types.append('DSA')
    if trade_types_sdb.fu_disc:
        trade_types.append('FUCD')
    if trade_types_sdb.fu_dma:
        trade_types.append('FUDMA')
    if trade_types_sdb.fu_dsa:
        trade_types.append('FUDSA')
    return '&'.join(trade_types)


def trade_types_to_str(trade_types):
    trade_types_str = []
    for key, product in __PRODUCT_DICT.items():
        t_types = trade_types.filter(product=product)
        if t_types:
            t_types_str = []
            for t_type in t_types:
                if t_type.handlinst.name == 'DISC':
                    t_types_str.append('CD')
                else:
                    t_types_str.append(t_type.handlinst.name)
            trade_types_str.append(''.join((key.upper(), '(', '&'.join(t_types_str), ')')))
    return '&'.join(trade_types_str)
