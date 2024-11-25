from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .forms import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from .models import *
from django.contrib import messages
from datetime import date

#login
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")
            return HttpResponseRedirect('/')
        else:
            messages.error(request, "Credenciales incorrectas. Inténtalo de nuevo.")
    else:
        form =  CustomLoginForm()
    return render(request, 'auth/login.html', {'form': form})

# Vista para Registro
def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Guarda el usuario pero no lo envía aún a la base de datos
            user.save()  # Ahora guarda el usuario en la base de datos
            messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
            return redirect('login')  # Redirige al login después de un registro exitoso
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = CustomRegisterForm()
    return render(request, 'auth/register.html', {'form': form})

# Vista para el Logout
@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')


def index(request):
    return render(request, 'principal/index.html')  # Asegúrate de usar la ruta correcta

#Lista de Usuarios
@login_required
@permission_required('auth.view_user', raise_exception=True)
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'biblioteca/usuarios/lista.html', {'usuarios': usuarios})

#Asignar Grupos
@login_required
@permission_required('auth.change_user', raise_exception=True)
def asignar_grupo(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    grupos = Group.objects.all()

    if request.method == 'POST':
        grupo_id = request.POST.get('grupo')
        grupo = get_object_or_404(Group, id=grupo_id)
        usuario.groups.clear()
        usuario.groups.add(grupo)
        messages.success(request, f"Grupo '{grupo.name}' asignado a {usuario.username}.")
        return redirect('lista_usuarios')

    return render(request, 'biblioteca/usuarios/asignar_grupo.html', {'usuario': usuario, 'grupos': grupos})

#Gestión de Libros


#Lista de Libros
@login_required
@permission_required('biblioteca.view_libro', raise_exception=True)
def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'biblioteca/libros/lista.html', {'libros': libros})

#Crear Libro
@login_required
@permission_required('biblioteca.add_libro', raise_exception=True)
def crear_libro(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        isbn = request.POST.get('isbn')
        if Libro.objects.filter(isbn=isbn).exists():
            messages.error(request, 'El libro con ese ISBN ya existe.')
        else:
            Libro.objects.create(
                titulo=titulo,
                isbn=isbn,
                fecha_publicacion=request.POST.get('fecha_publicacion')
            )
            messages.success(request, 'Libro creado exitosamente.')
            return redirect('lista_libros')
    return render(request, 'biblioteca/libros/crear.html')

#Préstamos
@login_required
@permission_required('biblioteca.add_prestamo', raise_exception=True)
def registrar_prestamo(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        ejemplar_id = request.POST.get('ejemplar')
        usuario = get_object_or_404(Usuario, id=usuario_id)
        ejemplar = get_object_or_404(Ejemplar, id=ejemplar_id, disponible=True)
        Prestamo.objects.create(usuario=usuario, ejemplar=ejemplar)
        ejemplar.disponible = False
        ejemplar.save()
        messages.success(request, f"Préstamo registrado para {usuario.username}.")
        return redirect('lista_prestamos')

    usuarios = Usuario.objects.all()
    ejemplares = Ejemplar.objects.filter(disponible=True)
    return render(request, 'biblioteca/prestamos/registrar.html', {'usuarios': usuarios, 'ejemplares': ejemplares})

#Lista de Préstamos
@login_required
@permission_required('biblioteca.view_prestamo', raise_exception=True)
def lista_prestamos(request):
    prestamos = Prestamo.objects.select_related('usuario', 'ejemplar').all()
    return render(request, 'biblioteca/prestamos/lista.html', {'prestamos': prestamos})

#Reservas y Lista de Espera

#Registrar Reserva
@login_required
@permission_required('biblioteca.add_reserva', raise_exception=True)
def registrar_reserva(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        ejemplar_id = request.POST.get('ejemplar')
        usuario = get_object_or_404(Usuario, id=usuario_id)
        ejemplar = get_object_or_404(Ejemplar, id=ejemplar_id)
        Reserva.objects.create(usuario=usuario, ejemplar=ejemplar)
        messages.success(request, f"Reserva registrada para {usuario.username}.")
        return redirect('lista_reservas')

    usuarios = Usuario.objects.all()
    ejemplares = Ejemplar.objects.all()
    return render(request, 'biblioteca/reservas/registrar.html', {'usuarios': usuarios, 'ejemplares': ejemplares})

#Lista de Espera
@login_required
@permission_required('biblioteca.view_listaespera', raise_exception=True)
def lista_espera(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    lista = reserva.lista_espera.all().order_by('posicion')
    return render(request, 'biblioteca/lista_espera/lista.html', {'reserva': reserva, 'lista': lista})
