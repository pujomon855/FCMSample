from dataclasses import dataclass, field
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from typing import NamedTuple

from .models import ClientClassifier, CodeSession, Client, ClientInfo, ClientTrade, ClientView, TradeType


class IndexView(generic.TemplateView):
    template_name = 'clients/index.html'


class ColGroup(NamedTuple):
    name: str
    css_classes: tuple = tuple()

    @property
    def css_classes_str(self):
        """
        このグループのカラムに追加するcssクラスの文字列
        :return: このグループのカラムに追加するcssクラスの文字列
        """
        return ' '.join(self.css_classes)


class Column(NamedTuple):
    name: str
    group: ColGroup


class Cell(NamedTuple):
    value: str
    url_info: dict = None


@dataclass
class ClientTableRecord:
    _COL_GRP_NONE = ColGroup('', ('col-grp-none',))
    _COL_GRP_FIX = ColGroup('FIX', ('col-grp-fix',))
    _COL_GRP_OMS = ColGroup('OMS', ('col-grp-oms',))

    # key:Column、item: Cell
    # itemの戻り値は、属性値自身とリンク先の情報(なければNone)のタプル
    _CL_TAB_COL_VALUES = {
        Column('Client Name', _COL_GRP_NONE):
            lambda record: Cell(record.name, {'url': 'clients:detail', 'args': record.id}),
        Column('View', _COL_GRP_NONE): lambda record: Cell(record.view),
        Column('Session', _COL_GRP_FIX): lambda record: Cell(record.session),
        Column('Session Start End', _COL_GRP_FIX): lambda record: Cell(record.session_start_end),
        Column('Code', _COL_GRP_FIX): lambda record: Cell(record.code),
        Column('TradeType(Possible)', _COL_GRP_OMS): lambda record: Cell(record.products),
        Column('EQ Limit Daily(Disc)', _COL_GRP_OMS): lambda record: Cell(record.eq_lmt_1day_disc),
        Column('EQ Limit Daily(DMA)', _COL_GRP_OMS): lambda record: Cell(record.eq_lmt_1day_dma),
        Column('EQ Limit Daily(DSA)', _COL_GRP_OMS): lambda record: Cell(record.eq_lmt_1day_dsa),
        Column('EQ Limit 1Shot(Disc)', _COL_GRP_OMS): lambda record: Cell(record.eq_lmt_1shot_disc),
        Column('EQ Limit 1Shot(DMA)', _COL_GRP_OMS): lambda record: Cell(record.eq_lmt_1shot_dma),
        Column('EQ Limit 1Shot(DSA)', _COL_GRP_OMS): lambda record: Cell(record.eq_lmt_1shot_dsa),
        Column('FU Limit Daily(Disc)', _COL_GRP_OMS): lambda record: Cell(record.fu_lmt_1day_disc),
        Column('FU Limit Daily(DMA)', _COL_GRP_OMS): lambda record: Cell(record.fu_lmt_1day_dma),
        Column('FU Limit Daily(DSA)', _COL_GRP_OMS): lambda record: Cell(record.fu_lmt_1day_dsa),
        Column('FU Limit 1Shot(Disc)', _COL_GRP_OMS): lambda record: Cell(record.fu_lmt_1shot_disc),
        Column('FU Limit 1Shot(DMA)', _COL_GRP_OMS): lambda record: Cell(record.fu_lmt_1shot_dma),
        Column('FU Limit 1Shot(DSA)', _COL_GRP_OMS): lambda record: Cell(record.fu_lmt_1shot_dsa),
    }
    _CL_TAB_COL_NAMES = _CL_TAB_COL_VALUES.keys()
    _CL_TAB_FUNCS = _CL_TAB_COL_VALUES.values()

    id: str
    name: str
    view: str
    session: str
    session_start_end: str
    code: str
    products: str
    eq_lmt_1day_disc: str = ''
    eq_lmt_1day_dma: str = ''
    eq_lmt_1day_dsa: str = ''
    eq_lmt_1shot_disc: str = ''
    eq_lmt_1shot_dma: str = ''
    eq_lmt_1shot_dsa: str = ''
    fu_lmt_1day_disc: str = ''
    fu_lmt_1day_dma: str = ''
    fu_lmt_1day_dsa: str = ''
    fu_lmt_1shot_disc: str = ''
    fu_lmt_1shot_dma: str = ''
    fu_lmt_1shot_dsa: str = ''

    @classmethod
    def column_names(cls):
        """
        顧客テーブルのColumnのリストを返す
        :return: 顧客テーブルのColumnのリスト
        """
        return cls._CL_TAB_COL_NAMES

    @classmethod
    def column_groups(cls):
        return [cls._COL_GRP_NONE, cls._COL_GRP_FIX, cls._COL_GRP_OMS]

    def __iter__(self):
        for func in self._CL_TAB_FUNCS:
            yield func(self)


class ClientTableView(generic.ListView):
    template_name = 'clients/table.html'
    context_object_name = 'client_list'

    def get_queryset(self):
        clients = Client.objects.order_by('name')
        client_records = []
        for client in clients:
            classifiers = ClientClassifier.objects.filter(client=client)
            for classifier in classifiers:
                code_sessions = CodeSession.objects.filter(code=classifier)
                for code_session in code_sessions:
                    session = code_session.session
                    session_start_end = '-'.join((str(session.start_time), str(session.end_time)))
                    csp_list = TradeType.objects.filter(code=classifier).filter(session=session)
                    products = ', '.join([f'{csp.product}({csp.handlinst})' for csp in csp_list])
                    record = ClientTableRecord(
                        client.id, client.name, classifier.view, session, session_start_end, classifier, products)
                    self._set_limits(classifier.identifier, record)
                    client_records.append(record)
        return client_records

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['columns'] = ClientTableRecord.column_names()
        return context

    def _set_limits(self, client_id, record):
        """
        行データに注文の上限を設定する。

        :param client_id: 顧客ID
        :param record: 行データ
        """
        limits = ClientView.objects.using('limit').filter(client_id=client_id)
        for limit in limits:
            if limit.product == 'Equity':
                if limit.handlinst == 'Disc':
                    if limit.limit_type == '1':
                        record.eq_lmt_1shot_disc = limit.order_limit
                    else:
                        record.eq_lmt_1day_disc = limit.order_limit
                elif limit.handlinst == 'DMA':
                    if limit.limit_type == '1':
                        record.eq_lmt_1shot_dma = limit.order_limit
                    else:
                        record.eq_lmt_1day_dma = limit.order_limit
                else:
                    if limit.limit_type == '1':
                        record.eq_lmt_1shot_dsa = limit.order_limit
                    else:
                        record.eq_lmt_1day_dsa = limit.order_limit
            else:
                if limit.handlinst == 'Disc':
                    if limit.limit_type == '1':
                        record.fu_lmt_1shot_disc = limit.order_limit
                    else:
                        record.fu_lmt_1day_disc = limit.order_limit
                elif limit.handlinst == 'DMA':
                    if limit.limit_type == '1':
                        record.fu_lmt_1shot_dma = limit.order_limit
                    else:
                        record.fu_lmt_1day_dma = limit.order_limit
                else:
                    if limit.limit_type == '1':
                        record.fu_lmt_1shot_dsa = limit.order_limit
                    else:
                        record.fu_lmt_1day_dsa = limit.order_limit


def show_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    # 暫定的に1つ目のClientClassifier使用
    classifier = client.clientclassifier_set.first()
    limits = ClientView.objects.using('limit').filter(client_id=classifier.identifier)
    return render(request, 'clients/detail.html', {
        'client': client, 'limits': limits
    })


# For admin form
def get_trade_type(request):
    trade_type = {
        'trade_type': '',
    }
    if request.method == 'GET':
        key = request.GET.get('key')
        value = request.GET.get('value')
        try:
            if key:
                if key == 'client_id':
                    client_id = value
                else:
                    client_info = ClientInfo.objects.using('limit').get(view=value) if key == 'view' \
                        else ClientInfo.objects.using('limit').get(code=value)
                    client_id = client_info.client_id
                client_data = ClientTrade.objects.using('limit').filter(client_id=client_id)
                trade_type['trade_type'] = client_data_to_str(client_data)
        except (ClientInfo.DoesNotExist, ClientTrade.DoesNotExist):
            pass
    return JsonResponse(trade_type)


def client_data_to_str(client_data):
    if client_data.exists():
        data = client_data[0]
        trade_types = []
        if data.is_disc:
            trade_types.append('DISC')
        if data.is_dma:
            trade_types.append('DMA')
        if data.is_dsa:
            trade_types.append('DSA')
        return ', '.join(trade_types)
    return ''
