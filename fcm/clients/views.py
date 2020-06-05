from dataclasses import dataclass
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
import openpyxl
import os
from typing import NamedTuple

from fcm import settings
from .models import ClientClassifier, CodeSession, Client, ClientInfo, ClientTrade, ClientView, TradeType
from .models import Product, HandlInst
from .forms import ClientForm, ViewCodeForm, ViewCodeSessionForm, SessionTradeTypeForm


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


class IndexView(generic.TemplateView):
    template_name = 'clients/index.html'


class ColGroup(NamedTuple):
    name: str
    grp_class: str


class Column(NamedTuple):
    name: str
    group: ColGroup


class Cell(NamedTuple):
    value: str
    url_info: dict = None


@dataclass
class ClientTableRecord:
    _COL_GRP_CLIENT = ColGroup('Client', 'col-grp-client')
    _COL_GRP_FIX = ColGroup('FIX', 'col-grp-fix')
    _COL_GRP_OMS = ColGroup('OMS', 'col-grp-oms')

    # key:Column、item: Cell
    # itemの戻り値は、属性値自身とリンク先の情報(なければNone)のタプル
    _CL_TAB_COL_VALUES = {
        Column('Client Name', _COL_GRP_CLIENT):
            lambda record: Cell(record.name, {'url': 'clients:detail', 'args': record.id}),
        Column('View', _COL_GRP_CLIENT): lambda record: Cell(record.view),
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
        return [cls._COL_GRP_CLIENT, cls._COL_GRP_FIX, cls._COL_GRP_OMS]

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
        context['col_groups'] = ClientTableRecord.column_groups()
        return context

    @staticmethod
    def _set_limits(client_id, record):
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
        if data.eq_disc:
            trade_types.append('DISC')
        if data.eq_dma:
            trade_types.append('DMA')
        if data.eq_dsa:
            trade_types.append('DSA')
        return ', '.join(trade_types)
    return ''


# ------------------------------------------------
# Add/Edit/Delete Client Data
# ------------------------------------------------

def add_client(request):
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        view_code_form = ViewCodeForm(request.POST)
        view_code_session_form = ViewCodeSessionForm(request.POST)
        session_trade_type_form = SessionTradeTypeForm(request.POST)

        # フォーム単体の入力チェック
        if client_form.is_valid() and view_code_form.is_valid() and \
                view_code_session_form.is_valid() and session_trade_type_form.is_valid():
            is_valid = True
            # 入力データの組み合わせでのエラーチェック
            client_id = view_code_form["identifier"].value()  # identifierはhidden fieldのためcleaned_dataから取得できない
            client = get_existing_client(client_form.cleaned_data['name'])
            classifier = get_existing_client_classifier(client_id)
            session = view_code_session_form.cleaned_data['session']
            if classifier:
                # 他の顧客と紐づいていないかチェック
                if client and classifier.client.name != client.name:
                    view_err_msg = f'{classifier.view} is already linked to {classifier.client.name}.'
                    view_code_form.add_error('view', view_err_msg)
                    is_valid = False
                # ViewCodeとSessionの組み合わせがすでに存在しているかチェック
                if CodeSession.objects.filter(code=classifier, session=session).exists():
                    session_err_msg = f'The combination of {classifier.code} and {session} is already exists.'
                    view_code_session_form.add_error('session', session_err_msg)
                    is_valid = False

            # データの組み合わせに問題がない場合のみ保存処理を実行
            if is_valid:
                # 顧客は新規の場合のみ保存
                if client is None:
                    client = client_form.save()

                # 顧客識別情報に、顧客とhidden fieldであるclient_idを設定して保存
                client_classifier = view_code_form.save(commit=False)
                client_classifier.client = client
                client_classifier.identifier = client_id
                client_classifier.save()

                # ViewCode、Sessionを設定して保存
                view_code_session = view_code_session_form.save(commit=False)
                view_code_session.code = client_classifier
                view_code_session.session = session
                view_code_session.save()

                save_trade_types(classifier, session, session_trade_type_form)

    else:
        client_form = ClientForm()
        view_code_form = ViewCodeForm()
        view_code_session_form = ViewCodeSessionForm()
        session_trade_type_form = SessionTradeTypeForm()

    context = {
        'client_form': client_form,
        'view_code_form': view_code_form,
        'view_code_session_form': view_code_session_form,
        'session_trade_type_form': session_trade_type_form,
    }

    return render(request, 'clients/add_client.html', context)


def get_existing_client(client_name):
    """
    顧客名から既存の顧客を取得する。
    指定顧客名の顧客が存在しない場合はNoneを返す。

    :param client_name: 顧客名
    :return: 顧客
    """
    if Client.objects.filter(name=client_name).exists():
        return Client.objects.get(name=client_name)
    return None


def get_existing_client_classifier(client_id):
    """
    顧客IDから顧客識別子情報を取得する。
    指定IDが存在しない場合はNoneを返す。

    :param client_id: 顧客ID
    :return: 顧客識別子情報
    """
    if ClientClassifier.objects.filter(identifier=client_id).exists():
        return ClientClassifier.objects.get(identifier=client_id)
    return None


def save_trade_types(classifier, session, session_trade_type_form):
    """
    取引形態を保存する

    :param classifier: 顧客識別情報
    :param session: セッション
    :param session_trade_type_form: 取引形態入力フォーム
    """
    eq = __PRODUCT_DICT.get('eq')
    fu = __PRODUCT_DICT.get('fu')
    op = __PRODUCT_DICT.get('op')
    sp = __PRODUCT_DICT.get('sp')
    disc = __HANDLINST_DICT.get('disc')
    dma = __HANDLINST_DICT.get('dma')
    dsa = __HANDLINST_DICT.get('dsa')

    _save_trade_type(session_trade_type_form.cleaned_data['eq_disc'], classifier, session, eq, disc)
    _save_trade_type(session_trade_type_form.cleaned_data['eq_dma'], classifier, session, eq, dma)
    _save_trade_type(session_trade_type_form.cleaned_data['eq_dsa'], classifier, session, eq, dsa)
    _save_trade_type(session_trade_type_form.cleaned_data['fu_disc'], classifier, session, fu, disc)
    _save_trade_type(session_trade_type_form.cleaned_data['fu_dma'], classifier, session, fu, dma)
    _save_trade_type(session_trade_type_form.cleaned_data['fu_dsa'], classifier, session, fu, dsa)
    _save_trade_type(session_trade_type_form.cleaned_data['op_disc'], classifier, session, op, disc)
    _save_trade_type(session_trade_type_form.cleaned_data['op_dma'], classifier, session, op, dma)
    _save_trade_type(session_trade_type_form.cleaned_data['op_dsa'], classifier, session, op, dsa)
    _save_trade_type(session_trade_type_form.cleaned_data['sp_disc'], classifier, session, sp, disc)
    _save_trade_type(session_trade_type_form.cleaned_data['sp_dma'], classifier, session, sp, dma)
    _save_trade_type(session_trade_type_form.cleaned_data['sp_dsa'], classifier, session, sp, dsa)


def _save_trade_type(flag, classifier, session, product, handlinst):
    if flag:
        trade_type = TradeType(code=classifier, session=session, product=product, handlinst=handlinst)
        trade_type.save()


def get_client_info(request):
    client_info = {
        'exists': False
    }
    if request.method == 'GET':
        key = request.GET.get('key')
        value = request.GET.get('value')
        try:
            if key:
                if key == 'view_code':
                    info = ClientInfo.objects.using('limit').get(view=value)
                else:
                    info = ClientInfo.objects.using('limit').get(code=value)
                trade = ClientTrade.objects.using('limit').get(client_id=info.client_id)
                client_info['exists'] = True
                client_info['client_id'] = info.client_id
                client_info['view_code'] = info.view
                client_info['fix_code'] = info.code
                client_info['eq_disc'] = trade.eq_disc
                client_info['eq_dma'] = trade.eq_dma
                client_info['eq_dsa'] = trade.eq_dsa
                client_info['fu_disc'] = trade.fu_disc
                client_info['fu_dma'] = trade.fu_dma
                client_info['fu_dsa'] = trade.fu_dsa
        except (ClientInfo.DoesNotExist, ClientTrade.DoesNotExist):
            pass
    return JsonResponse(client_info)


# ------------------------------------------------
# Export Client Table
# ------------------------------------------------
def export_client_table(request):
    if request.method == 'POST':
        file_path = os.path.join(settings.BASE_DIR, 'clients\\static\\clients\\excel\\FIXClientTable.xlsx')
        print(f'{file_path=}')
        wb = openpyxl.load_workbook(file_path)
        sheet = wb['Clients']
        sheet['A3'] = 1
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=FIXClientTable.xlsx'
        wb.save(response)
        return response
    return HttpResponse()
