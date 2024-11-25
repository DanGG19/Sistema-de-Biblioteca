from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import date
from decimal import Decimal


class BaseModel(models.Model):
    """
    Modelo base para agregar campos de auditoría y timestamps a todas las entidades.
    """
    creado = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    actualizado = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    class Meta:
        abstract = True  # No se crea tabla para este modelo


class Usuario(AbstractUser):
    """
    Extiende el modelo de usuario de Django para incluir campos adicionales.
    """
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    es_empleado = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text="Los grupos a los que pertenece este usuario.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text="Permisos específicos para este usuario.",
    )

    def __str__(self):
        return f"{self.username} (Grupos: {', '.join([group.name for group in self.groups.all()])})"


class Autor(BaseModel):
    """
    Representa a un autor de uno o más libros.
    """
    nombre = models.CharField(max_length=255)
    biografia = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Editorial(BaseModel):
    """
    Representa a la editorial que publica los libros.
    """
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Categoria(BaseModel):
    """
    Categoriza los libros en géneros o temas.
    """
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Libro(BaseModel):
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
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)

    def disponibilidad(self):
        """
        Calcula la cantidad de ejemplares disponibles para el libro.
        """
        return self.ejemplares.filter(disponible=True).count()

    def __str__(self):
        return self.titulo


class Ejemplar(BaseModel):
    """
    Representa una copia física o digital de un libro.
    """
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ejemplares')
    codigo_barras = models.CharField(max_length=30, unique=True)
    ubicacion = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)
    formato = models.CharField(max_length=50, choices=[('Físico', 'Físico'), ('Digital', 'Digital')])
    estado = models.CharField(max_length=50, choices=[('Nuevo', 'Nuevo'), ('Bueno', 'Bueno'), ('Dañado', 'Dañado')])

    def __str__(self):
        return f"{self.libro.titulo} - {self.codigo_barras}"


class Prestamo(BaseModel):
    """
    Registra el préstamo de un ejemplar a un usuario.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='prestamos')
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='prestamos')
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)

    def calcular_multa(self):
        """
        Calcula la multa en base a días de retraso en la devolución.
        """
        if not self.fecha_devolucion and not self.devuelto:
            dias_retraso = (date.today() - self.fecha_prestamo).days - 14  # Ejemplo: 14 días de préstamo permitido
            return max(Decimal(dias_retraso * 0.50), Decimal(0))  # Multa de 0.50 por día
        return Decimal(0)

    def __str__(self):
        return f"Préstamo de {self.ejemplar} a {self.usuario}"


class Multa(BaseModel):
    """
    Representa una multa aplicada a un usuario por retrasos en devoluciones.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='multas')
    prestamo = models.OneToOneField(Prestamo, on_delete=models.CASCADE, related_name='multa')
    monto = models.DecimalField(max_digits=6, decimal_places=2)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Multa de {self.monto} para {self.usuario}"


class Reserva(BaseModel):
    """
    Registra la reserva de un ejemplar por parte de un usuario.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Reserva de {self.ejemplar} por {self.usuario}"


class ListaEspera(BaseModel):
    """
    Registra la lista de espera de usuarios para un ejemplar reservado.
    """
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='lista_espera')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    posicion = models.PositiveIntegerField()  # Orden en la lista de espera

    class Meta:
        unique_together = ('reserva', 'usuario')  # Un usuario solo puede estar una vez en la lista de espera para una reserva

    def __str__(self):
        return f"Usuario {self.usuario} en posición {self.posicion} de la lista de espera para {self.reserva.ejemplar}"


class Reporte:
    """
    Métodos estáticos para generar reportes y estadísticas.
    """
    @staticmethod
    def libros_mas_prestados():
        return Libro.objects.annotate(
            total_prestamos=models.Count('ejemplares__prestamos')
        ).order_by('-total_prestamos')[:10]

    @staticmethod
    def usuarios_mas_activos():
        return Usuario.objects.annotate(
            total_prestamos=models.Count('prestamos')
        ).order_by('-total_prestamos')[:10]
