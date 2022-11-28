from flask import Flask
import requests
from config import Config

app = Flask(__name__)


@app.route("/listar_empleados/<string:dependencia>", methods=["GET"])
def lectura_empleados(dependencia):
    try:
        if dependencia == "direccion de sistemas":
            resultado = requests.get("http://127.0.0.1:5000/users")
        elif dependencia == "Superior tribunal de just.":
            resultado = requests.get("http://127.0.0.1:4000/users")

        resultado_json = resultado.json()
        json = resultado_json['user_list']
        return {dependencia:json}
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)


@app.route("/listar_asistencias/<string:dependencia>", methods=["GET"])
def enviar_asistencia(dependencia):
    try:
        if dependencia == "direccion de sistemas":
            resultado = requests.get("http://127.0.0.1:5000/fetch")
        elif dependencia == "Superior tribunal de just.":
            resultado = requests.get("http://127.0.0.1:4000/fetch")
        resultado_json = resultado.json()
        json = resultado_json['attendances']
        #return f'Fecha y hora: {json["timestamp"]}'#
        return {dependencia:json}
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)

@app.route("/listar_asistencias", methods=["GET"])
def enviar_asistencia_todas():
    try:
        resultado_dep1 = requests.get("http://127.0.0.1:5000/fetch")
        resultado_dep2 = requests.get("http://127.0.0.1:4000/fetch")
        dependencia1 = "direccion de sistemas"
        dependencia2 = "Superior tribunal de just."

        resultado_json_dep1 = resultado_dep1.json()
        resultado_json_dep2 = resultado_dep2.json()
        json1 = resultado_json_dep1['attendances']
        json2 = resultado_json_dep2['attendances']
        #return f'Fecha y hora: {json["timestamp"]}'#
        return {dependencia1:json1, dependencia2:json2}
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)
    

@app.route("/agregar_empleado/<string:nombre_empleado>/<string:id_empleado>/<string:dependencia>", methods=["POST"])
def agregar_empleado(nombre_empleado, id_empleado, dependencia):
    try:
        if dependencia == "direccion de sistemas":
            resultado = requests.post("http://127.0.0.1:5000/crear/" + str(nombre_empleado) + "/" + str(id_empleado))
        elif dependencia == "Superior tribunal de just.":
            resultado = requests.post("http://127.0.0.1:5000/crear/" + str(nombre_empleado) + "/" + str(id_empleado))
        resultado_json = resultado.json()
        return resultado_json
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)


@app.route("/enrolar_empleado/<string:id_empleado>/<string:dependencia>", methods=["POST"])
def enrolar_empleado(id_empleado, dependencia):
    try:
        if dependencia == "direccion de sistemas":
            resultado = requests.post("http://127.0.0.1:5000/enroll/" + str(id_empleado))
        elif dependencia == "Superior tribunal de just.":
            resultado = requests.post("http://127.0.0.1:5000/enroll/" + str(id_empleado))
        resultado_json = resultado.json()
        return resultado_json
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)


@app.route('/editar_empleado/<string:nombre_empleado>/<string:id_empleado>/<string:dependencia>', methods=['PUT'])
def editar_empleado(nombre_empleado, id_empleado, dependencia):
    try:
        if dependencia == "direccion de sistemas":
            resultado = requests.put("http://127.0.0.1:5000/actualizar_user/" + str(id_empleado) + "/" + str(nombre_empleado))
        elif dependencia == "Superior tribunal de just.":
            resultado = requests.put("http://127.0.0.1:4000/actualizar_user/" + str(id_empleado) + "/" + str(nombre_empleado))
        resultado_json = resultado.json()
        return resultado_json
    except requests.exceptions.RequestException as e:  
        raise SystemExit(e)


if __name__ == "__main__":
    app.config.from_object(Config["development"])
    app.run(debug=True, host='0.0.0.0', port=3000)