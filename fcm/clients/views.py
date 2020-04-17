from dataclasses import dataclass
from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import ClientClassifier, CodeSession, Client, ClientLimit, TradeType


class IndexView(generic.TemplateView):
    template_name = 'clients/index.html'


@dataclass
class ClientTableRecord:
    id: int
    name: str
    session: str
    session_start_end: str
    code: str
    products: str


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
                    record = ClientTableRecord(client.id, client.name, session, session_start_end, classifier, products)
                    client_records.append(record)
        return client_records


def show_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    # 暫定的に1つ目のClientClassifier使用
    classifier = client.clientclassifier_set.first()
    limits = ClientLimit.objects.using('limit').filter(client_id=classifier.identifier)
    return render(request, 'clients/detail.html', {
        'client': client, 'limits': limits
    })
