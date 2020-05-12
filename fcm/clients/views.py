from dataclasses import dataclass
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import ClientClassifier, CodeSession, Client, ClientInfo, ClientTrade, ClientView, TradeType


class IndexView(generic.TemplateView):
    template_name = 'clients/index.html'


@dataclass
class ClientTableRecord:
    # key:カラム名、item: カラム名に紐づくこのクラスの属性値の取得関数
    # itemの戻り値は、属性値自身とリンク先の情報(なければNone)のタプル
    _CL_TAB_COL_VALUES = {
        'Client Name': lambda record: (record.name, {'url': 'clients:detail', 'args': record.id}),
        'Session': lambda record: (record.session, None),
        'Session Start End': lambda record: (record.session_start_end, None),
        'Code': lambda record: (record.code, None),
        'Products': lambda record: (record.products, None),
    }
    _CL_TAB_COL_NAMES = _CL_TAB_COL_VALUES.keys()
    _CL_TAB_FUNCS = _CL_TAB_COL_VALUES.values()

    id: str
    name: str
    session: str
    session_start_end: str
    code: str
    products: str

    @classmethod
    def column_names(cls):
        """
        顧客テーブルのカラム名のリストを返す
        :return: 顧客テーブルのカラム名のリスト
        """
        return cls._CL_TAB_COL_NAMES

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
                        client.id, client.name, session, session_start_end, classifier, products)
                    client_records.append(record)
        return client_records

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['col_names'] = ClientTableRecord.column_names()
        return context


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
