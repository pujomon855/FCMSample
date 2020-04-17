from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=30)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class HandlInst(models.Model):
    name = models.CharField(max_length=5)
    value = models.IntegerField()

    def __str__(self):
        return self.name


class ClientClassifier(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    identifier = models.CharField(max_length=20)
    code = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.client}: {self.identifier}, {self.code}'


class CodeSession(models.Model):
    code = models.ForeignKey(ClientClassifier, on_delete=models.PROTECT)
    session = models.ForeignKey(Session, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.code}, {self.session}'


class Logic(models.Model):
    name = models.CharField(max_length=20)
    definition = models.TextField(max_length=300)

    def __str__(self):
        return self.name


class CodeSessionLogic(models.Model):
    code = models.ForeignKey(ClientClassifier, on_delete=models.PROTECT)
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    logic = models.ForeignKey(Logic, on_delete=models.PROTECT)
    in_out = models.CharField(max_length=2, choices=[
        ('IN', 'in'), ('OT', 'out'),
    ])

    def __str__(self):
        return f'{self.session}, {self.code}, {self.in_out}, {self.logic}'


class TradeType(models.Model):
    code = models.ForeignKey(ClientClassifier, on_delete=models.PROTECT)
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    handlinst = models.ForeignKey(HandlInst, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.code}, {self.session}, {self.product}, {self.handlinst}'


class ClientLimit(models.Model):
    client_id = models.CharField(primary_key=True, max_length=20)
    product = models.CharField(max_length=20)
    handlinst = models.CharField(max_length=5)
    limit_type = models.CharField(max_length=1)
    order_limit = models.IntegerField(blank=True, null=True)
    type1 = models.CharField(max_length=5, blank=True, null=True)
    type2 = models.CharField(max_length=5, blank=True, null=True)
    type3 = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ClientLimit'
        unique_together = (('client_id', 'product', 'handlinst', 'limit_type'),)
