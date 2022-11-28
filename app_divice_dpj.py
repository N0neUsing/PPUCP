# -*- coding: utf-8 -*-
import json, sys, datetime
from pickle import TRUE
from pytz import timezone
from zk import ZK, const
from functools import wraps
from flask import Flask, jsonify, abort, request
import pytz

if sys.version_info.major < 3:
    reload(sys)



sys.path.append("zk")

zk = ZK('192.168.16.99', port=4370, timeout=5)
def create_app():
    settings = {
        'DEBUG': False,
    }
    app = Flask(__name__)
    app.config.update(settings)
    return app


app = create_app()

#confiugracion de hora y fecha
conn = None                         #se conecta a zk
print ('Connecting to device ...')         
conn = zk.connect()                        
print ('Disabling device ...')
conn.disable_device()
last_updated = datetime.datetime.now(pytz.utc)
formato = "%d-%m-%Y %H:%M:%S"
now_utc = datetime.datetime.now(timezone('GMT'))
now_argentina = now_utc.astimezone(timezone('America/Argentina/Buenos_Aires'))
timestamp = now_argentina.strftime(formato)
conn.set_time(now_argentina) 

#Método Actualizar Cambios del Dispositivo:
                                                         
#Este método tomará los datos de las bases de datos locales de los dispositivos que la poseen.
#Datos referidos a su asistencia, id persona, fecha y hora, dependencia, y el tipo de dato según el dispositivo (la huella digital, id tarjeta magnética).                                       

@app.route('/users', methods=['GET'])   #se crea una ruta para listar los usuarios cargados con todos los datos 
                                        
def listar_usuarios():                  #se define fucnion listar usuario
    
    conn = None                         #se conecta a zk
    print ('Connecting to device ...')         
    conn = zk.connect()                        
    print ('Disabling device ...')
    conn.disable_device()
    
    users_data = conn.get_users()               #user_data almacena los datos debueltos por la funcion get_users
    users = []                                  #se crea lista
    for data in users_data:                     #se recorre users_data buscando data
        user = {}                               #se crea un diccionario para insertar los datos 
        user['u_id'] = data.uid             
        user['nombre'] = data.name
        user['user_id'] = data.user_id
        user['privilege'] = data.privilege
        user['password'] = data.password
        user['group_id'] = data.group_id  
        user['temp_id'] = str(conn.get_user_template(uid=data.uid,temp_id=0, user_id = data.user_id)   )          
        users.append(user)                       #se agrega a la lista el diccionario creado con los datos
    user_list = users 
    last_updated = datetime.datetime.now(pytz.utc)
    return jsonify(user_list = user_list, last_updated = last_updated.isoformat())

#ruta para crear o insertar un nuevo usuario
#datos del usuario nesesarios en la ruta para registrarlo
 
#id_user        / id del usuario a incorporar
#privilege_user / privilegios del usuario si es usuario normal o admin
#group_id_user  / noc a que se refiere
#password_user  / contraseña si es que se registra la asistencia con numeros
#card_user      / codigo de la tergeta del usuario o empleado en el caso que tenga
#full_name      / nombre completo del empleado o usuaroio

@app.route('/crear/<string:nombre>/<string:user_id>', methods=['POST'])
def crear_usuario(nombre,user_id):
    conn = None
    zk = ZK('192.168.16.99', port=4370, timeout=5)
    try:
        print ('Connecting to device ...')
        conn = zk.connect()
        print ('Disabling device ...')
        uid = None
        privilege = 0
        password = ""
        group_id = ""
        card = 0
        users_data = conn.get_users()
        users = []
        for data in users_data:
            user = {}
            user['user_id'] = data.user_id
            users.append(user)
        usuario_encontrado = [data for data in users if data['user_id'] == user_id]
        if len(usuario_encontrado) > 0:
            return jsonify('El usuario ya existe')
        else:
            conn.set_user(uid, nombre, privilege, password, group_id, user_id, card)
            return jsonify('Usuario enrolado con éxito')

    except Exception as e:
        print ("Process terminate : {}".format(e))
    finally:
        if conn:
            conn.disconnect()

#Método Actualizar Cambios del Dispositivo:
# se crea una ruta para actualizar de una persona
#datos nesesarios para actualizar datos de una persona existente

#full_name     / nombre completo de la usuario
#id_user     / id del usuario existente

@app.route('/actualizar_user/<string:id_users>/<string:full_names>', methods=['PUT'])                                                                                    #intento de enroll_user
                                                                                    
def insert_actu_user( id_users, full_names): 
    conn=None
    print ('Connecting to device ...')         
    conn = zk.connect()    
    conn.disable_device()                 
    users_id_very = id_users                    #user_id_very/se guarda id para verificar si existe antes de cargar

    user_data= conn.get_users()                     #se llama a la funion get_users, para traer los usuarios                                                #se almacenan en user data
    for data in user_data:                          #se recorre user_data
        if users_id_very == data.user_id :           #se pregunta si ya existe esa id
                user_id = data.user_id
                privilege = data.privilege           #se guardan los datos
                password = data.password
                group_id = data.group_id 
                uid = data.uid
                card = data.card
                name =  full_names  
                conn.delete_user(uid,user_id )                           #se elimina el usuario         
                conn.set_user(uid,name, privilege, password, group_id, user_id, card)   #se envian los datos actualizados para el dispositivo      
                return ('Usuario actualizado')    #se emite un aviso
#Enrrolamiento de la huella de una persona existente    
@app.route('/enroll/<string:id_users>', methods=['POST'])   #se crea una ruta para enrolar una huella/ no se espesifca que huella
                                                                #en un id usuario o persona existente en el dispositivo
                                                                
def enroll_usuario(id_users):                              #se define una funcion enrolar usuario y se le pasa un aparametro,
                                                                #este parametro es la variable en la que se guarda el ID que se envio 
    conn = None
    print ('Connecting to device ...')
    conn = zk.connect()                                                                              
    uid = None
    temp_id =0
    user_id = id_users
    very = conn.enroll_user(uid, temp_id, user_id)                #se envia a la funcion enrrioll_user tres parametros el uid que da el disposistivo
    conn.disable_device()
    print ('aaaaaaa ...')
    return jsonify('Enr_Ok')
 
 #Listado de asistencias           
@app.route('/fetch', methods=['GET'])
def fetch_attendances():
    conn = None
    global attendances
    global last_updated
    
    try:
        print ('Connecting to device ...')
        conn = zk.connect()
        print ('Disabling device ...')
        conn.disable_device()
        attendance_data = conn.get_attendance()
        attends = []
        for data in attendance_data:
            attendance = {}
            attendance['user_id'] = data.user_id
            attendance['status'] = data.status
            attendance['timestamp'] = (data.timestamp).strftime(formato)
            attends.append(attendance)
        attendances = attends
        last_updated = datetime.datetime.now(zk.UTC -3)
    except Exception as e:
        print ( "Process terminate : {}".format(e))
    finally:
        print ('Enabling device ...')
        conn.enable_device()
        print ('Disconnect from device')
        if conn:
            conn.disconnect()
    return jsonify(attendances = attendances, last_updated = last_updated.isoformat())

if __name__ == '__main__':
    app.run( debug= True)
