# models.py
# -*- coding: utf-8 -*-
import peewee
import datetime
import hashlib

database = peewee.SqliteDatabase("caja.db")

class Cotona(peewee.Model):
    """
    ORM model of album table
    """
    name = peewee.CharField()
    block = peewee.CharField()
    date = peewee.DateTimeField()

    class Meta:
        database = database

class Primo(peewee.Model):

    name = peewee.CharField(primary_key=True)
    debe = peewee.IntegerField()
    pagado = peewee.IntegerField()
    total = peewee.IntegerField()

    class Meta:
        database = database

class Activo(peewee.Model):

    id = peewee.IntegerField(primary_key=True)
    #Nombre de la persona que arrienda
    name = peewee.CharField()
    #Ya sea cotona o impresion
    tipo_ingreso = peewee.CharField()
    #La hora donde ocurrio
    date = peewee.DateTimeField()
    #A tiempo o atrasado
    estado = peewee.CharField()

    class Meta:
        database = database

class Impresion(peewee.Model):

    tipo_impresion = peewee.CharField()
    numero_paginas = peewee.IntegerField()
    total = peewee.IntegerField()
    date = peewee.DateTimeField()

    class Meta:
        database = database

class Ingresos(peewee.Model):

    #Nombre de la persona que retira/ingresa
    name = peewee.CharField()
    #Ya sea ingreso o retiro
    tipo = peewee.CharField()
    #A tiempo o atrasado
    monto = peewee.IntegerField()
    #La hora donde ocurrio
    date = peewee.DateTimeField()

    class Meta:
        database = database

class Cuenta(peewee.Model):
    #Clave primaria autoincremental
    id = peewee.IntegerField(primary_key=True)
    #Ya sea cotona o impresion
    tipo_ingreso = peewee.CharField()
    #Monto Total
    monto = peewee.IntegerField()
    #Cantidad
    cantidad = peewee.IntegerField()
    #La hora donde ocurrio
    date = peewee.DateTimeField()

    class Meta:
        database = database

class User(peewee.Model):
    id = peewee.IntegerField(primary_key=True)
    user = peewee.CharField(unique=True)
    password = peewee.CharField()
    created_date = peewee.DateField()

    class Meta:
        database = database

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

if __name__ == "__main__":
    try:
        Cotona.create_table()
    except peewee.OperationalError:
        print "Tabla Cotona ya existe"
    try:
        Primo.create_table()
    except peewee.OperationalError:
        print "Tabla Primo ya existe"
    try:
        Cuenta.create_table()
    except peewee.OperationalError:
        print "Tabla Cuenta ya existe"
    try:
        Activo.create_table()
    except peewee.OperationalError:
        print "Tabla Activo ya existe"
    try:
        Ingresos.create_table()
    except peewee.OperationalError:
        print "Tabla Ingresos ya existe"
    try:
        Impresion.create_table()
    except peewee.OperationalError:
        print "Tabla Impresion ya existe"
    try:
        User.create_table()
    except peewee.OperationalError:
        print "Tabla User ya existe"

    primos = [{"name": "Blac",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Cheko",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Diego",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Rene",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Canario",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Nix",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Karu",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Neko",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Nacho",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Pollo",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Zippy",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Feño",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Feña",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Maipu",
           "debe": 0,
           "pagado": 0,
           "total": 0},
          {"name": "Joaco",
           "debe": 0,
           "pagado": 0,
           "total": 0}
          ]
    Primo.insert_many(primos).execute()
    usuarios = User(user="root", password=hashlib.sha256("inuneko").hexdigest(), created_date=datetime.datetime.now())
    usuarios.save()