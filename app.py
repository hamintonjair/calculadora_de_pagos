from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import math

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.calculadora_db
contratos = db.contratos

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.nombre = user_data['nombre']
        self.apellido = user_data['apellido']
        self.cedula = user_data.get('cedula', '')
        self.telefono = user_data.get('telefono', '')
        self.direccion = user_data.get('direccion', '')

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        print(f"Error al cargar usuario: {e}")
        return None

def calcular_duracion(fecha_inicio, fecha_fin):
    inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    diff = abs((fin - inicio).days)
    meses = diff // 30
    dias = diff % 30
    
    if meses == 0:
        return f'{dias} días'
    elif dias == 0:
        return f'{meses} meses'
    else:
        return f'{meses} meses y {dias} días'

def convertir_dias_a_texto(dias):
    meses = dias // 30  # Aproximar a meses (30 días por mes)
    dias_restantes = dias % 30
    partes = []
    if meses > 0:
        partes.append(f"{meses} mes{'es' if meses > 1 else ''}")
    if dias_restantes > 0:
        partes.append(f"{dias_restantes} día{'s' if dias_restantes > 1 else ''}")
    return ", ".join(partes) if partes else "0 días"

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = db.users.find_one({'email': email})
            if user and check_password_hash(user['password'], password):
                user_obj = User(user)
                login_user(user_obj)
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('calculadora'))
            else:
                flash('Correo electrónico o contraseña incorrectos.', 'danger')
        except Exception as e:
            print(f"Error en login: {e}")
            flash('Ocurrió un error al intentar iniciar sesión.', 'danger')
    
    return render_template('login.html')

@app.route('/calculadora')
@login_required
def calculadora():
    # Obtener parámetros de la URL
    valor_contrato = request.args.get('valorContrato', '').replace('.', '').replace(',', '')
    valor_mensual = request.args.get('valorMensual', '').replace('.', '').replace(',', '')
    fecha_inicio = request.args.get('fechaInicio', '')
    fecha_fin = request.args.get('fechaFin', '')

    # Si tenemos todos los parámetros, calcular
    if valor_contrato and valor_mensual and fecha_inicio and fecha_fin:
        try:
            # Convertir valores a números
            valor_contrato = int(valor_contrato)
            valor_mensual = int(valor_mensual)

            # Convertir fechas del formato dd/mm/yyyy a fecha
            def convertir_fecha(fecha):
                partes = fecha.split('/')
                if len(partes) == 3:
                    return datetime(int(partes[2]), int(partes[1]), int(partes[0]))
                return datetime.strptime(fecha, '%Y-%m-%d')

            inicio = convertir_fecha(fecha_inicio)
            fin = convertir_fecha(fecha_fin)

            # Calcular días totales y duración en texto
            dias_totales = (fin - inicio).days + 1
            duracion_texto = convertir_dias_a_texto(dias_totales)

            # Generar lista de meses
            meses = []
            fecha_actual = inicio
            while fecha_actual <= fin:
                meses.append({
                    'fecha_inicio': fecha_actual.strftime('%d/%m/%Y'),
                    'fecha_fin': (fecha_actual + timedelta(days=30-1)).strftime('%d/%m/%Y'),
                    'dias': 30,
                    'valor_mensual': valor_mensual,
                    'valor_diario': round(valor_mensual / 30, 2),
                    'total': valor_mensual + round(valor_mensual * 0.19),
                    'saldo': valor_contrato,
                    'porcentaje': 0,
                    'porcentaje_acumulado': 0,
                    'valor_pago': valor_mensual
                })
                # Avanzar al siguiente mes
                if fecha_actual.month == 12:
                    fecha_actual = datetime(fecha_actual.year + 1, 1, 1)
                else:
                    fecha_actual = datetime(fecha_actual.year, fecha_actual.month + 1, 1)

            # Calcular pagos por mes
            pago_acumulado = 0
            porcentaje_acumulado = 0

            for i, mes in enumerate(meses):
                year = mes['fecha_inicio'].split('/')[2]
                month = mes['fecha_inicio'].split('/')[1]

                # Determinar período
                inicio_mes = inicio if i == 0 else datetime(int(year), int(month), 1)
                
                if i == len(meses) - 1:
                    fin_mes = fin
                else:
                    # Siempre considerar hasta el día 30 del mes
                    fin_mes = datetime(int(year), int(month) + 1, 1) - timedelta(days=1)  # Último día del mes
                    if fin_mes.day > 30:
                        fin_mes = datetime(int(year), int(month), 30)

                # Calcular días siempre considerando 30 días como máximo
                dias_mes = min((fin_mes - inicio_mes).days + 1, 30)

                # Cálculo del pago
                if i == len(meses) - 1:
                    # Último pago
                    pago_mes = min(valor_mensual, valor_contrato - pago_acumulado)
                else:
                    if inicio_mes.day == 1 and fin_mes.day == 30:
                        pago_mes = valor_mensual  # Mes completo
                    else:
                        # Prorrateo basado siempre en 30 días
                        pago_mes = round((valor_mensual / 30) * dias_mes)

                # Calcular porcentajes y valores
                porcentaje_mes = (pago_mes / valor_contrato) * 100
                pago_acumulado += pago_mes
                porcentaje_acumulado += porcentaje_mes
                saldo_restante = max(0, valor_contrato - pago_acumulado)

                # Calcular IVA
                iva = round(pago_mes * 0.19)
                total = pago_mes + iva

                meses[i]['fecha_inicio'] = inicio_mes.strftime('%d/%m/%Y')
                meses[i]['fecha_fin'] = fin_mes.strftime('%d/%m/%Y')
                meses[i]['dias'] = dias_mes
                meses[i]['total'] = total
                meses[i]['saldo'] = saldo_restante
                meses[i]['porcentaje'] = math.ceil(porcentaje_mes * 100) / 100
                meses[i]['porcentaje_acumulado'] = math.ceil(porcentaje_acumulado * 100) / 100
                meses[i]['valor_pago'] = pago_mes

            # Calcular diferencia entre valor contrato y total de meses pagados
            total_meses_pagados = sum(pago['valor_pago'] for pago in meses)
            diferencia = valor_contrato - total_meses_pagados

            # Preparar datos para la plantilla
            datos = {
                'valor_contrato': valor_contrato,
                'valor_mensual': valor_mensual,
                'fecha_inicio': inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fin.strftime('%d/%m/%Y'),
                'dias_totales': dias_totales,
                'duracion': duracion_texto,
                'valor_diario': round(valor_mensual / 30, 2),
                'pagos': meses,
                'diferencia': diferencia
            }

            return render_template('calculadora.html', datos=datos)

        except Exception as e:
            print(f"Error en cálculos: {str(e)}")
            flash('Error al realizar los cálculos. Por favor, verifique los datos ingresados.', 'error')

    # Si no hay parámetros o hubo error, mostrar formulario vacío
    datos = contratos.find_one({'usuario_id': str(current_user.id)}, sort=[('_id', -1)])
    if datos:
        datos['valor_contrato'] = "{:,.0f}".format(datos['valor_contrato'])
        datos['valor_mensual'] = "{:,.0f}".format(datos['valor_mensual'])
    return render_template('calculadora.html', datos=datos)

@app.route('/guardar_contrato', methods=['POST'])
def guardar_contrato():
    try:
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        valor_contrato = float(request.form['valor_contrato'].replace(',', ''))
        valor_mensual = float(request.form['valor_mensual'].replace(',', ''))
        
        duracion = calcular_duracion(fecha_inicio, fecha_fin)
        
        contrato = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'valor_contrato': valor_contrato,
            'valor_mensual': valor_mensual,
            'duracion': duracion,
            'usuario_id': str(current_user.id)
        }
        
        contratos.insert_one(contrato)
        flash('Contrato guardado exitosamente', 'success')
        return redirect(url_for('calculadora'))
    except Exception as e:
        flash(f'Error al guardar el contrato: {str(e)}', 'error')
        return redirect(url_for('calculadora'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))
        
    if request.method == 'POST':
        try:
            user_data = {
                'nombre': request.form.get('nombre'),
                'apellido': request.form.get('apellido'),
                'cedula': request.form.get('cedula'),
                'email': request.form.get('email'),
                'telefono': request.form.get('telefono'),
                'direccion': request.form.get('direccion'),
                'password': generate_password_hash(request.form.get('password'))
            }
            
            if db.users.find_one({'email': user_data['email']}):
                flash('Este correo electrónico ya está registrado.', 'warning')
                return redirect(url_for('registro'))
            if db.users.find_one({'cedula': user_data['cedula']}):
                flash('Esta cédula ya está registrada.', 'warning')
                return redirect(url_for('registro'))
            
            db.users.insert_one(user_data)
            flash('¡Registro exitoso! Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error en registro: {e}")
            flash('Ocurrió un error al intentar registrarse.', 'danger')
    
    return render_template('registro.html')

@app.route('/actualizar_perfil', methods=['GET', 'POST'])
@login_required
def actualizar_perfil():
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password')
            user = db.users.find_one({'_id': ObjectId(current_user.id)})
            
            if not check_password_hash(user['password'], current_password):
                flash('La contraseña actual es incorrecta.', 'danger')
                return redirect(url_for('actualizar_perfil'))

            user_data = {
                'nombre': request.form.get('nombre'),
                'apellido': request.form.get('apellido'),
                'cedula': request.form.get('cedula'),
                'email': request.form.get('email'),
                'telefono': request.form.get('telefono'),
                'direccion': request.form.get('direccion')
            }
            
            # Si se proporciona una nueva contraseña, actualizarla
            new_password = request.form.get('new_password')
            if new_password:
                user_data['password'] = generate_password_hash(new_password)
            
            db.users.update_one(
                {'_id': ObjectId(current_user.id)},
                {'$set': user_data}
            )
            flash('Tu perfil ha sido actualizado exitosamente.', 'success')
            return redirect(url_for('calculadora'))
        except Exception as e:
            flash('Error al actualizar el perfil: ' + str(e), 'danger')
            return redirect(url_for('actualizar_perfil'))
    
    # Para GET, obtener los datos actuales del usuario
    user = db.users.find_one({'_id': ObjectId(current_user.id)})
    return render_template('actualizar_perfil.html', user=user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)