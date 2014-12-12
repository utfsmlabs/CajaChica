# -*- coding: utf-8 -*-

from flask import Flask, flash, redirect, url_for, render_template, request
import peewee
import datetime
from models import Cotona, Primo, Cuenta, Activo, Ingresos, Impresion, User
from wtforms import Form, TextField, validators, IntegerField, SelectField, StringField, PasswordField
from flask_login import LoginManager, login_user, current_user
import hashlib

app = Flask(__name__)

database = peewee.SqliteDatabase("caja.db")

app.secret_key ='asdjsdbfkasdbgkjasdgbadghfghfghdsgbj'

login_manager = LoginManager()
login_manager.init_app(app)

class CotonasForm(Form):
    name = TextField(u'Nombre', [validators.Length(min=4, max=45, message="Nombre muy corto (o muy largo).")])

class IngresoForm(Form):
    name = SelectField(u'Nombre', choices=[('Blac', 'Blac'), ('Canario', 'Canario'), ('Cheko', 'Cheko'),
                                           ('Diego', 'Diego'),  ('Feno', 'Feno'), ('Fena', 'Fena'), ('Joaco', 'Joaco'),
                                           ('Karu', 'Karu'), ('Maipu', 'Maipu'), ('Nacho', 'Nacho'),('Neko', 'Neko'),
                                           ('Nix', 'Nix'), ('Pollo', 'Pollo'), ('Rene', 'Rene'), ('Zippy', 'Zippy')])
    monto = IntegerField(u'Monto', [validators.NumberRange(min=0, max=None, message="Numero no valido.")])

class ImpresionForm(Form):
    tipo = SelectField(u'Opción', choices=[('Simplex', 'Simplex'), ('Duplex', 'Duplex'), ('Color', 'Color'),
                                           ('DVD', 'DVD')])
    paginas = IntegerField(u'Numero de Unidades', [validators.NumberRange(min=0, max=None, message="Numero no valido.")])

class LoginForm(Form):
    username = StringField(u'Usuario', validators=[validators.DataRequired()])
    password = PasswordField(u'Password', validators=[validators.DataRequired()])

@login_manager.user_loader
def load_user(id):
    try:
        return User.get(id=int(id))
    except User.DoesNotExist:
        return None

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template('login.html', form=form)
    else:
        username = form.username.data
        password = hashlib.sha256(form.password.data).hexdigest()
        user = User.get(user=username, password=password)
        if user is None:
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('login'))
        login_user(user)
        flash("Logged in successfully.")
        return redirect(url_for("index"))

#Ingreso de nuevo cotona
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CotonasForm(request.form)
    if request.method == 'POST' and form.validate():
        #Se ingresa cotona al historial
        arriendo = Cotona(name=form.name.data, block="3-4", date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        arriendo.save()
        #Se ingresa cotona como ingreso
        cuenta = Cuenta(tipo_ingreso="cotona", monto=500, cantidad=1, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cuenta.save()
        #Se deja el arriendo como activo
        activo = Activo(name=form.name.data, tipo_ingreso="cotona", date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), estado="OK")
        activo.save()
        if current_user.is_authenticated():
            return render_template('listacotonas.html', cotonas=Cotona.select())
        else:
            return redirect(url_for("login"))
    if current_user.is_authenticated():
        return render_template('register.html', form=form)
    else:
        return redirect(url_for("login"))

#Ingreso de dinero por parte de un primo
@app.route('/nuevodinero', methods=['GET', 'POST'])
def nuevodinero():
    form = IngresoForm(request.form)
    if request.method == 'POST' and form.validate():
        primo = Primo.get(Primo.name == form.name.data)
        #Se deja en el historial el nuevo ingreso
        ingresar = Ingresos(name=form.name.data, tipo="Ingreso", monto=form.monto.data, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ingresar.save()
        primo.pagado = primo.pagado + form.monto.data
        primo.total = primo.debe - primo.pagado
        #Se hace efectivo el ingreso de dinero
        pago = Primo.update(pagado=primo.pagado, total=primo.total).where(Primo.name == form.name.data)
        pago.execute()
        if current_user.is_authenticated():
            return render_template('ingresosretiros.html', ingresos=Ingresos.select())
        else:
            return redirect(url_for("login"))
    if current_user.is_authenticated():
        return render_template('nuevodinero.html', form=form)
    else:
        return redirect(url_for("login"))

#Retiro de dinero por parte de un primo
@app.route('/nuevoretiro', methods=['GET', 'POST'])
def nuevoretiro():
    form = IngresoForm(request.form)
    if request.method == 'POST' and form.validate():
        primo = Primo.get(Primo.name == form.name.data)
        total = 0
        debe = 0
        cuentas = Cuenta.select()
        #Se obtiene el total de la caja (NOTA: hay que hacer una funcion de esto
        for cuenta in cuentas:
            total = total + cuenta.monto
        ingresos = Ingresos.select()
        for ingres in ingresos:
            if ingres.tipo == "Ingreso":
                debe = debe + ingres.monto
            else:
                debe = debe - ingres.monto
        total = total + debe
        #Se compara, para saber si se saca mas de lo que existe en la caja
        if form.monto.data < total:
            primo.debe = primo.debe + form.monto.data
            primo.total = primo.debe - primo.pagado
            #Se hace efectivo el retiro en la cuenta del primo
            saca = Primo.update(debe=primo.debe, total=primo.total).where(Primo.name == form.name.data)
            saca.execute()
            #Se hace efectivo el retiro de dinero y se deja en el historial
            retiro = Ingresos(name=form.name.data, tipo="Retiro", monto=form.monto.data, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            retiro.save()
            return render_template('ingresosretiros.html', ingresos=Ingresos.select())
        else:
            if current_user.is_authenticated():
                return render_template('nuevoretiro.html', form=form,correcto=False)
            else:
                return redirect(url_for("login"))
    if current_user.is_authenticated():
        return render_template('nuevoretiro.html', form=form, correcto=True)
    else:
        return redirect(url_for("login"))
#
@app.route('/nuevaimpresion', methods=['GET', 'POST'])
def nuevaimpresion():
    form = ImpresionForm(request.form)
    if request.method == 'POST' and form.validate():
        #Se ingresa impresion historial
        if form.tipo.data == "Simplex":
            imprimir = Impresion(tipo_impresion=form.tipo.data, numero_paginas=form.paginas.data, total=form.paginas.data*20,
                                 date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            imprimir.save()
            cuenta = Cuenta(tipo_ingreso="Impresion Simplex", monto=form.paginas.data*20, cantidad=form.paginas.data,
                            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cuenta.save()
        #se hace efectivo la impresion en duplex
        if form.tipo.data == "Duplex":
            imprimir = Impresion(tipo_impresion=form.tipo.data, numero_paginas=form.paginas.data, total=form.paginas.data*30,
                                 date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            imprimir.save()
            cuenta = Cuenta(tipo_ingreso="Impresion Duplex", monto=form.paginas.data*30, cantidad=form.paginas.data,
                            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cuenta.save()
        #se hace efectivo la impresion a color
        if form.tipo.data == "Color":
            imprimir = Impresion(tipo_impresion=form.tipo.data, numero_paginas=form.paginas.data, total=form.paginas.data*50,
                                 date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            imprimir.save()
            cuenta = Cuenta(tipo_ingreso="Impresion Color", monto=form.paginas.data*50, cantidad=form.paginas.data,
                            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cuenta.save()
        #Se hace efectivo la compra de dvd
        if form.tipo.data == "DVD":
            imprimir = Impresion(tipo_impresion=form.tipo.data, numero_paginas=form.paginas.data, total=form.paginas.data*350,
                                 date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            imprimir.save()
            cuenta = Cuenta(tipo_ingreso="DVD", monto=form.paginas.data*350, cantidad=form.paginas.data,
                            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cuenta.save()
        #Se ingresa cotona como ingreso
        if current_user.is_authenticated():
            return render_template('impresiones.html', impresiones=Impresion.select())
        else:
            return redirect(url_for("login"))
    if current_user.is_authenticated():
        return render_template('nuevaimpresion.html', form=form)
    else:
        return redirect(url_for("login"))
#paginacion de cotonas
@app.route('/listacotonas', defaults={'listacotonas': 1},methods=['GET', 'POST'])
@app.route('/listacotonas/<int:listacotonas>', methods=['GET', 'POST'])
def show(listacotonas):
    if current_user.is_authenticated():
        return render_template('listacotonas.html', cotonas=Cotona.select().paginate(listacotonas, 10))
    else:
        return redirect(url_for("login"))

#paginacion de cuentas generales
@app.route('/cuentas', defaults={'cuentas': 1}, methods=['GET', 'POST'])
@app.route('/cuentas/<int:cuentas>', methods=['GET', 'POST'])
def show2(cuentas):
    if current_user.is_authenticated():
        return render_template('cuentas.html', cuentas=Cuenta.select().paginate(cuentas, 10))
    else:
        return redirect(url_for("login"))

#paginacion de ingresos/retiros
@app.route('/ingresosretiros', defaults={'ingresosretiros': 1}, methods=['GET', 'POST'])
@app.route('/ingresosretiros/<int:ingresosretiros>', methods=['GET', 'POST'])
def ingreso(ingresosretiros):
    if current_user.is_authenticated():
        return render_template('ingresosretiros.html', ingresos=Ingresos.select().paginate(ingresosretiros, 10))
    else:
        return redirect(url_for("login"))

#paginacion de impresiones/DVD
@app.route('/impresiones', defaults={'impresiones': 1}, methods=['GET', 'POST'])
@app.route('/impresiones/<int:impresiones>', methods=['GET', 'POST'])
def impresio(impresiones):
    if current_user.is_authenticated():
        return render_template('impresiones.html', impresiones=Impresion.select().paginate(impresiones, 10))
    else:
        return redirect(url_for("login"))
#index
@app.route('/')
@app.route('/index')
def index():
    #Se toma el total en caja
    total = 0
    debe = 0
    cuentas = Cuenta.select()
    for cuenta in cuentas:
        total = total + cuenta.monto
    ingresos = Ingresos.select()
    for ingres in ingresos:
        if ingres.tipo == "Ingreso":
            debe = debe + ingres.monto
        else:
            debe = debe - ingres.monto
    total = total + debe
    #Guaton Conversion
    guaton = round(total/8400)
    if current_user.is_authenticated():
        return render_template('index.html', activos=Activo.select(), ingresos=Ingresos.select().order_by(Ingresos.date.desc())
                               .paginate(1, 7),primos=Primo.select().order_by(Primo.total.desc()), total=total,
                               debe=-debe, guaton=guaton)
    else:
        return redirect(url_for("login"))

#Esta seccion esta en construccion, se supone que sirve para devolver las cotonas, pero aun no lo tengo implementado
#Lo mas probable es que use una herramienta no contemplada en el curso, o sea, lo hago despues.
@app.route('/entregarcotona/<int:id>')
def index2(id):
    borrar = Activo.delete().where(Activo.id == id)
    borrar.execute()
    total = 0
    debe = 0
    cuentas = Cuenta.select()
    for cuenta in cuentas:
        total = total + cuenta.monto
    ingresos = Ingresos.select()
    for ingres in ingresos:
        if ingres.tipo == "Ingreso":
            debe = debe + ingres.monto
        else:
            debe = debe - ingres.monto
    total = total + debe
    guaton = round(total/8400)
    if current_user.is_authenticated():
        return render_template('index.html', activos=Activo.select(), ingresos=Ingresos.select().order_by(Ingresos.date.desc())
                               .paginate(1, 7),primos=Primo.select().order_by(Primo.total.desc()), total=total,
                               debe=-debe, guaton=guaton)
    else:
        return redirect(url_for("login"))

#main duh
if __name__ == '__main__':
    app.debug = True
    app.run()