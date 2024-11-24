from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """
    Extiende el modelo de usuario de Django para incluir campos adicionales.
    """
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    es_empleado = models.BooleanField(depytfault=False)

    def __str__(self):
        return self.username

class Autor(models.Model):
    """
    Representa a un autor de uno o más libros.
    """
    nombre = models.CharField(max_length=255)
    biografia = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Editorial(models.Model):
    """
    Representa a la editorial que publica los libros.
    """
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    """
    Categoriza los libros en géneros o temas.
    """
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Libro(models.Model):
    """
    Representa la información bibliográfica de un libro.
    """
    titulo = models.CharField(max_length=255)
    autores = models.ManyToManyField(Autor, related_name='libros')
    editorial = models.ForeignKey(Editorial, on_delete=models.SET_NULL, null=True, related_name='libros')
    fecha_publicacion = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    categorias = models.ManyToManyField(Categoria, related_name='libros')
    sinopsis = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.titulo

class Ejemplar(models.Model):
    """
    Representa una copia física o digital de un libro.
    """
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ejemplares')
    codigo_barras = models.CharField(max_length=30, unique=True)
    ubicacion = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)
    formato = models.CharField(max_length=50, choices=[('Físico', 'Físico'), ('Digital', 'Digital')])

    def __str__(self):
        return f"{self.libro.titulo} - {self.codigo_barras}"

class Prestamo(models.Model):
    """
    Registra el préstamo de un ejemplar a un usuario.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='prestamos')
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='prestamos')
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"Préstamo de {self.ejemplar} a {self.usuario}"

class Reserva(models.Model):
    """
    Registra la reserva de un ejemplar por parte de un usuario.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Reserva de {self.ejemplar} por {self.usuario}"
