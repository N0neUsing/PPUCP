# -*- coding: utf-8 -*-
import json, sys, pytz, datetime
from zk import ZK, const
from functools import wraps

from flask import Flask, jsonify, abort, request
if sys.version_info.major < 3:
    reload(sys)
sys.path.append("zk")

user_list = []
attendances = []
last_updated = datetime.datetime.now(pytz.utc)

def create_app():

    settings = {
        'DEBUG': False,
    }

    app = Flask(__name__)
    app.config.update(settings)

    return app

app = create_app()

@app.route('/attendances', methods=['GET'])
def list_attendances():
    return jsonify(attendances = attendances, last_updated = last_updated.isoformat())

@app.route('/fetch', methods=['GET'])
def fetch_attendances():
    conn = None
    global attendances
    global last_updated
    zk = ZK('192.168.16.99', port=4370, timeout=5)
    try:
        print ('Connecting to device ...')
        conn = zk.connect()
        print ('Disabling device ...')
        conn.disable_device()
        attendance_data = conn.get_attendance()
        utc_tz = pytz.timezone('UTC')
        local_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        attends = []
        for data in attendance_data:
            attendance = {}
            attendance['user_id'] = data.user_id
            attendance['status'] = data.status
            attendance['timestamp'] = local_tz.localize(data.timestamp).astimezone(utc_tz).isoformat()
            attends.append(attendance)
        attendances = attends
        last_updated = datetime.datetime.now(pytz.utc)
    except Exception as e:
        print ("Process terminate : {}".format(e))
    finally:
        print ('Enabling device ...')
        conn.enable_device()
        print ('Disconnect from device ...')
        if conn:
            conn.disconnect()
    return jsonify(attendances = attendances, last_updated = last_updated.isoformat())

@app.route('/users', methods=['GET'])
def listar_usuarios():
    conn = None
    global user_list
    global attendances
    global last_updated
    zk = ZK('192.168.16.99', port=4370, timeout=5)
    try:
        print ('Connecting to device ...')
        conn = zk.connect()
        print ('Disabling device ...')
        conn.disable_device()
        users_data = conn.get_users()
        users = []
        for data in users_data:
            privilege = 'User'
            if data.privilege == const.USER_ADMIN:
                privilege = 'Admin'            
            user = {}
            user['u_id'] = data.uid
            user['nombre'] = data.name
            user['user_id'] = data.user_id
            user['privilegio'] = privilege
            users.append(user)
        user_list = users
        last_updated = datetime.datetime.now(pytz.utc)
    except Exception as e:
        print ("Process terminate : {}".format(e))
    finally:
        print ('Enabling device ...')
        conn.enable_device()
        print ('Disconnect from device ...')
        if conn:
            conn.disconnect()
    return jsonify(user_list = user_list, last_updated = last_updated.isoformat())

@app.route('/fetch/<string:user_id>', methods=['DELETE'])
def deleteAttendance(user_id):
    attendanceFound = [data for data in attendances if data['user_id'] == user_id]
    if len(attendanceFound) > 0:
        attendances.remove(attendanceFound[0])
    return jsonify(attendances = attendances, last_updated = last_updated.isoformat())

@app.route('/eliminarAsistencias', methods=['PUT'])
def eliminarAsistencia():
    conn = None
    global attendances
    global last_updated
    zk = ZK('192.168.16.99', port=4370, timeout=5)
    try:
        print ('Connecting to device ...')
        conn = zk.connect()
        print ('Disabling device ...')
        conn.disable_device()
        conn.clear_attendance()
    except Exception as e:
        print ("Process terminate : {}".format(e))
    finally:
        print ('Enabling device ...')
        conn.enable_device()
        print ('Disconnect from device ...')
        if conn:
            conn.disconnect()
    return jsonify(attendances = attendances, last_updated = last_updated.isoformat())

if __name__ == '__main__':
    app.run(debug=True)
