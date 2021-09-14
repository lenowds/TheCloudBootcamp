import requests
import json
import os
import string
import random
import base64
from flask import escape
from flask_cors import CORS, cross_origin
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

@cross_origin()
def recebe_requisicao(request):
    request_form = request.form

    if request_form and 'inputNome' and 'inputSobrenome' and 'inputEmail' in request_form:
        nome = request_form['inputNome']
        sobrenome = request_form['inputSobrenome']
        email = request_form['inputEmail']

        resultado = cria_usuario_moodle(email,nome,sobrenome)

        if resultado == 'sucesso':
        	return 'Solicitação recebida com sucesso.'
        else:
        	print('RR:ERRO:CRIACAO_DE_USUARIO_FALHOU')
        	return 'Erro, entre em contato com o administrator do sistema.'
    else:
        print('RR:ERRO:PARAMETRO_NAO_ENCONTRADO')
        return 'Erro, entre em contato com o administrator do sistema.'

def cria_usuario_moodle(email,nome,sobrenome):
	
	token = os.environ.get('MOODLE_TOKEN')
	servidor = os.environ.get('MOODLE_SERVER')

	function = 'core_user_create_users'
	url = 'http://{0}/webservice/rest/server.php?wstoken={1}&wsfunction={2}&moodlewsrestformat=json'.format(servidor,token,function)

	email = email
	username = email.split("@")[0]
	passw = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
	passw = base64.b64encode(passw.encode('ascii'))

	users = {'users[0][username]': username,
	        'users[0][email]': email,
	        'users[0][lastname]': sobrenome,
	        'users[0][firstname]': nome,
	        'users[0][password]': passw}

	try:
		sendmail(email, username, passw)
		response = requests.post(url,data=users)
		if 'exception' in json.loads(response.text):
			print('Result: ' + response.text)
			return 'erro'
		else:
			print('Result: ' + response.text)
			return 'sucesso'
	except Exception as e:
		print(e)
		return 'erro'

def sendmail(email, username, password):

    texto = '<br/><br/><center><b>Segue sua credencial de acesso ao moodle</b></center><br/><br/><strong>user:</strong> {0}<br/><strong>password:</strong> {1}<br/>'.format(username, password) 
    message = Mail(from_email='leniel1@hotmail.com',
                    to_emails=email,
                    subject='Credencial de acesso ao moodle',
                    html_content=texto)

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        
    except Exception as e:
        print(e)