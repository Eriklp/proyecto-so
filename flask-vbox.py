#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Librerias requeridas para correr aplicaciones basadas en Flask
from flask import Flask, jsonify, make_response, request, abort
import subprocess

app = Flask(__name__)



# Web service que se invoca al momento de ejecutar el comando
# curl http://localhost:5000
@app.route('/',methods = ['GET'])
def index():
	return "Hola Univalle"

# Este metodo retorna la lista de sistemas operativos soportados por VirtualBox
# Los tipos de sistemas operativos soportados deben ser mostrados al ejecutar 
# el comando
# curl http://localhost:5000/vms/ostypes
# Este es el codigo del item 1
@app.route('/vms/ostypes',methods = ['GET'])
def ostypes():
	output = subprocess.check_output(['VBoxManage','list', 'ostypes'])
	# Tu codigo aqui
	return output

# Este metodo retorna la lista de maquinas asociadas con un usuario al ejecutar
# el comando
# curl http://localhost:5000/vms
# Este es el codigo del item 2a
@app.route('/vms',methods = ['GET'])
def listvms():
	output = subprocess.check_output(['VBoxManage','list','vms'])
	#return jsonify({'lista de maquinas virtuales':output})
	return output

# Este metodo retorna aquellas maquinas que se encuentran en ejecucion al 
# ejecutar el comando
# curl http://localhost:5000/vms/running
# Este es el codigo del item 2b
@app.route('/vms/running',methods = ['GET'])
def runninglistvms():
	output = subprocess.check_output(['VBoxManage', 'list', 'runningvms'])
	# Tu codigo aqui
	return jsonify({'maquinas en ejecucion': output})

# Este metodo retorna las caracteristica de una maquina virtual cuyo nombre es
# vmname 
#al ejecutar el comando
#curl http://localhost:5000/vms/info/<vmname>
@app.route('/vms/info/<string:vmname>', methods = ['GET'])
def vminfo(vmname):
	lista = subprocess.Popen(['VBoxManage','list','vms'], stdout = subprocess.PIPE)
	cut = subprocess.Popen(['cut', '-d', ' ', '-f', '1'], stdin = lista.stdout, stdout = subprocess.PIPE)
	noms = subprocess.Popen(['grep', '-w', vmname], stdin = cut.stdout, stdout = subprocess.PIPE)
	nombre = subprocess.check_output(['uniq'], stdin = noms.stdout)
	if len(nombre) == 0:
		abort(404)
	else:
		vm = subprocess.Popen(['VBoxManage', 'showvminfo', vmname], stdout = subprocess.PIPE)
  		grep = subprocess.Popen(['grep', 'Name:'], stdin = vm.stdout, stdout = subprocess.PIPE)
  		name = subprocess.check_output(['cut', '-d', ' ', '-f', '13'], stdin = grep.stdout)
  		vm2 = subprocess.Popen(['VBoxManage', 'showvminfo', vmname], stdout = subprocess.PIPE)
  		grep2 = subprocess.Popen(['grep', 'Memory size:'], stdin = vm2.stdout, stdout = subprocess.PIPE)
  		memory = subprocess.check_output(['cut', '-d', ' ', '-f', '7'], stdin = grep2.stdout)
  		vm3 = subprocess.Popen(['VBoxManage', 'showvminfo', vmname], stdout = subprocess.PIPE)
  		grep3 = subprocess.Popen(['grep', 'Number of CPUs:'], stdin = vm3.stdout, stdout = subprocess.PIPE)
  		cpus = subprocess.check_output(['cut', '-d', ' ', '-f', '5'], stdin = grep3.stdout)
  		vm4 = subprocess.Popen(['VBoxManage', 'showvminfo', vmname], stdout = subprocess.PIPE)
  		grep4 = subprocess.Popen(['grep', 'Attachment:'], stdin = vm4.stdout, stdout = subprocess.PIPE)
  		red = subprocess.check_output(['cut', '-d', ':', '-f', '4'], stdin = grep4.stdout)
  		return jsonify({'nombre': name,  'CPUs': cpus, 'RAM': memory, 'Adap de red': red})
	
  
# Usted deberá realizar además los items 4 y 5 del enunciado del proyecto 
# considerando que:


# - El item 4 deberá usar el método POST del protocolo HTTP
#Este metodo crea una maquina virtual por medio del metodo POST
#al ejecutar el comando
#curl -i -X POST http://localhost:5000/vms/create/<nombre>/<ram>/<hd>/<cpus>
@app.route('/vms/create/<nombre>/<ram>/<hd>/<cpus>', methods = ['POST'])
def vmcreate(nombre, ram, hd, cpus):		
	info = subprocess.check_output(['/root/Escritorio/maquinavirtual.sh', nombre, ram, hd, cpus])
	return jsonify({'Se creo la maquina': nombre, 'RAM': ram, 'Disco': hd, 'CPUs': cpus})
	


# - El item 5 deberá usar el método DELETE del protocolo HTTP
#Este metodo elimina una maquina virtual por medio del metodo DELETE
#al ejecutar este comando 
#curl -i -X DELETE http://localhost:5000/vms/delete/<vmname>
@app.route('/vms/delete/<vmname>', methods = ['DELETE'])
def vmdelete(vmname):
	lista = subprocess.Popen(['VBoxManage','list','vms'], stdout = subprocess.PIPE)
	cut = subprocess.Popen(['cut', '-d', ' ', '-f', '1'], stdin = lista.stdout, stdout = subprocess.PIPE)
	noms = subprocess.Popen(['grep', '-w', vmname], stdin = cut.stdout, stdout = subprocess.PIPE)
	nombre = subprocess.check_output(['uniq'], stdin = noms.stdout)
	if len(nombre) == 0:
		abort(404)
	else:
		info = subprocess.check_output(['VBoxManage', 'unregistervm', vmname, '--delete'])	
		return jsonify({'Se elimino la maquina virtual': vmname})

#capturadores de errores 404 y 405
@app.errorhandler(404)
def not_foud(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

	
@app.errorhandler(405)
def not_foud(error):
	return make_response(jsonify({'error': 'Not Exist'}), 405)

if __name__ == '__main__':
        app.run(debug = True, host='0.0.0.0')
