# -*- coding: utf-8 -*-

import datetime
import jinja2
import os
import webapp2
import cgi

from google.appengine.api import users

#Vamos a usar el manejador de forms WTForms





#Importamos el módulo necesario para trabajar con la base de datos
from google.appengine.ext import ndb
'''
ndb es una libreria de modelado de datos, que corre completamente en el código de
nuestra aplicación. La librería fue iniciada por Guido van Rsossum.
'''


from webapp2_extras import sessions

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

#Creamos el modelo del objeto
class Player(ndb.Model):
    name = ndb.StringProperty()
    level = ndb.IntegerProperty()
    create_date = ndb.DateTimeProperty()

class Alumno(ndb.Model):

    nombre = ndb.StringProperty()
    apellidos = ndb.StringProperty()


template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.getcwd()))




class Formulario(webapp2.RequestHandler):

    def get(self):

        template=template_env.get_template('formulario.html')
        self.response.out.write(template.render())



    def post(self):

        def validaTexto(texto):
            if len(texto)>0:
                return True
            else:
                return False


        nombreUsuario = validaTexto(self.request.get('nombre'))
        apellidosUsuario = validaTexto(self.request.get('apellidos'))

        if not(nombreUsuario and apellidosUsuario):
            template=template_env.get_template('formulario.html')
            self.response.out.write(template.render())
        else:
            #Grabamos los datos en la base de datos.

            alumno= Alumno()
            alumno.nombre=self.request.get('nombre')
            alumno.apellidos=self.request.get('apellidos')
            alumno.put()

            #Enviamos mensaje de aceptación.
            self.response.out.write('<html><body>You wrote:<pre>')
            self.response.out.write(self.request.get('nombre'))
            self.response.out.write('</pre></body></html>')


class Alumnos(webapp2.RequestHandler):

    def get(self):

        alumnos = Alumno.query()
        resultados= alumnos.fetch(10)

        FAVORITES = [ "chocolates", "lunar eclipses", "rabbits" ]
        templateVars = {"favorites" : resultados}

        template = template_env.get_template('alumnos.html')
        #Cargamos la plantilla y le pasamos los datos cargardos
        self.response.out.write(template.render(templateVars))


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = template_env.get_template('inicio.html')
        '''
        user = self.session.get('user')
        template_values = {
            'user': user
            }
        '''
        self.response.out.write(template.render())

class MainPage2(webapp2.RequestHandler):
    def get(self):

        p1 = Player()
        p1.level=7
        p1.put()

        print p1

        current_time = datetime.datetime.now()
        user = users.get_current_user()
        login_url = users.create_login_url(self.request.path)
        logout_url = users.create_logout_url(self.request.path)

        template = template_env.get_template('home.html')
        context = {
            'current_time': current_time,
            'user': user,
            'login_url': login_url,
            'logout_url': logout_url,
        }
        self.response.out.write(template.render(context))

application = webapp2.WSGIApplication([
                                      ('/', MainPage),
                                      ('/form', Formulario),
                                      ('/alumnos', Alumnos)
                                      ]
                                      ,debug=True)
