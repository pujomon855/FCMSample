from dataclasses import dataclass
from django.views import generic

from .models import Code, Client, ClientLimit, Session, CodeSessionProduct


class IndexView(generic.TemplateView):
    template_name = 'clients/index.html'


@dataclass
class ClientTableRecord:
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
            session = Session.objects.get(id=client.session.id)
            session_start_end = '-'.join((str(session.start_time), str(session.end_time)))
            code = Code.objects.get(id=client.code.id)
            csp_list = CodeSessionProduct.objects.filter(code=code).filter(session=session)
            products = ', '.join([f'{csp.product}({csp.handlinst})' for csp in csp_list])
            record = ClientTableRecord(client.name, session, session_start_end, code, products)
            client_records.append(record)
        return client_records


class ClientDetailView(generic.DetailView):
    model = Client
    template_name = 'clients/detail.html'
    client = None

    def get_queryset(self):
        queryset = super().get_queryset()
        if queryset:
            self.client = queryset[0]
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        limits = []
        if self.client:
            limits = ClientLimit.objects.using('limit').filter(client_id=self.client.client_id)
        context['limits'] = limits
        return context
