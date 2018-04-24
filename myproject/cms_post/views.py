from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Page
import urllib.parse
import urllib.request
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

from django.template.loader import get_template
from django.template import Context

def auth(request):
    if request.user.is_authenticated():
        logged = 'Logged in as ' + request.user.username + "    " + "<a href= '/logout'>Logout</a>"
    else:
        logged = 'Not logged in.' + "<a href='/login'>Login</a>"
    return logged

def home(request):
    respuesta = "<ul>"
    for listado in Page.objects.all():
        respuesta += "<li><a href= '/" + str(listado.nombre) + "'>" + listado.nombre + '</a>'
    respuesta += "</ul>"
    logged = auth(request)
    return HttpResponse(logged + "<br><br>Contenido de la base de datos:<br>" + respuesta)

@csrf_exempt
def insertar(request, texto):
    logged = auth(request)

    if request.method == "GET":
        try:
            p = Page.objects.get(nombre = texto)
            return HttpResponse(logged + "<br><br>" + p.pagina)
        except Page.DoesNotExist:
            return HttpResponse(logged + "<br><br>No existe una página para ese recurso.")

    else:
        if request.user.is_authenticated():
            try:
                p = Page.objects.get(nombre = texto)
                p = Page(nombre = texto, pagina = request.body.decode('utf-8'))
                p.save()
                return HttpResponse("Página con el nombre: '" + str(p.nombre) + "' y el cuerpo: " + str(p.pagina) + " ha sido modificada.")
            except Page.DoesNotExist:
                p = Page(nombre = texto, pagina = request.body.decode('utf-8'))
                p.save()
                return HttpResponse("Página con el nombre: '" + str(p.nombre) + "' y el cuerpo: " + str(p.pagina) + " ha sido creada.")
        else:
            return HttpResponse(logged + "<br><br>Necesitas estar logueado para modificar una página")

def mostrar_temp(request, recurso):
    logged = auth(request)
    if request.user.is_authenticated():
        try:
            rec = Page.objects.get(nombre=recurso)
        except Page.DoesNotExist:
            return HttpResponse("Recurso no existente")

        try:
            template = get_template("RedTie/index.html")
            c = Context({'recurso': rec.nombre, 'body': rec.pagina,'logged': logged})
            return HttpResponse(template.render(c))
        except TemplateDoesNotExist:
            return HttpResponse("Error al obtener el template")
    else:
        return HttpResponse(logged)

@csrf_exempt
def modificar(request, recurso):
    logged = auth(request)

    try:
        n = Page.objects.get(nombre = recurso)
    except Page.DoesNotExist:
        return HttpResponse("Recurso no disponible en la base de datos.")

    if request.method == "GET":
        template = get_template("formulario/form.html")
        c = Context({'recurso': str(n.nombre), 'contenido': str(n.pagina)})
        return HttpResponse(template.render(c))
    elif request.method == "POST":
        n.pagina = urllib.parse.unquote(str(request.POST).split('=')[1][:-1])
        n.save()

        template = get_template("formulario/form.html")
        c = Context({'recurso': str(n.nombre), 'contenido': str(n.pagina)})
        return HttpResponse(template.render(c))
    else:
        return HttpResponse("Método no válido.")
