from django.db import models


class Code(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


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
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    code = models.ForeignKey(Code, on_delete=models.PROTECT)
    client_id = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class HandlInst(models.Model):
    name = models.CharField(max_length=5)
    value = models.IntegerField()

    def __str__(self):
        return self.name


class SessionProduct(models.Model):
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    handlinst = models.ForeignKey(HandlInst, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.session}: {self.product}, {self.handlinst}'


class Logic(models.Model):
    name = models.CharField(max_length=20)
    definition = models.TextField(max_length=300)

    def __str__(self):
        return self.name


class CodeSessionLogic(models.Model):
    code = models.ForeignKey(Code, on_delete=models.PROTECT)
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    logic = models.ForeignKey(Logic, on_delete=models.PROTECT)
    in_out = models.CharField(max_length=2, choices=[
        ('IN', 'in'), ('OT', 'out'),
    ])

    def __str__(self):
        return f'{self.session}, {self.code}, {self.in_out}, {self.logic}'


class CodeSessionProduct(models.Model):
    code = models.ForeignKey(Code, on_delete=models.PROTECT)
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    handlinst = models.ForeignKey(HandlInst, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.code}, {self.session}, {self.product}, {self.handlinst}'
