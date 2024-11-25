from django.urls import path
from . import views 
from .views import *

urlpatterns = [
    path('', views.index, name='index'),  # Página principal#
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:usuario_id>/asignar-grupo/', views.asignar_grupo, name='asignar_grupo'),
    path('libros/', views.lista_libros, name='lista_libros'),
    path('libros/crear/', views.crear_libro, name='crear_libro'),
    path('prestamos/', views.lista_prestamos, name='lista_prestamos'),
    path('prestamos/registrar/', views.registrar_prestamo, name='registrar_prestamo'),
    path('reservas/registrar/', views.registrar_reserva, name='registrar_reserva'),
    path('reservas/<int:reserva_id>/lista-espera/', views.lista_espera, name='lista_espera'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),

]
