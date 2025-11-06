"""
Modelos del Módulo de Gestión de Rutas
Siguiendo el patrón MVC y el principio de Responsabilidad Única (SRP)
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Cedis(models.Model):
    """
    Modelo para Centros de Distribución (CEDIS)
    Responsabilidad: Gestionar datos de centros de distribución
    """
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cedis'
        verbose_name = 'Centro de Distribución'
        verbose_name_plural = 'Centros de Distribución'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"


class Vendedor(models.Model):
    """
    Modelo para Vendedores
    Responsabilidad: Gestionar información de vendedores
    """
    nombre_completo = models.CharField(max_length=150)
    codigo_empleado = models.CharField(max_length=50, unique=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'vendedores'
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} ({self.codigo_empleado})"


class Cliente(models.Model):
    """
    Modelo para Clientes
    Responsabilidad: Gestionar información de clientes y su ubicación
    """
    nombre_comercial = models.CharField(max_length=200)
    direccion = models.TextField()
    latitud = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    longitud = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre_comercial']

    def __str__(self):
        return self.nombre_comercial

    @property
    def tiene_coordenadas(self):
        """Verifica si el cliente tiene coordenadas geográficas"""
        return self.latitud is not None and self.longitud is not None


class Ruta(models.Model):
    """
    Modelo principal para Rutas
    Responsabilidad: Gestionar rutas de distribución
    """
    DIAS_SEMANA = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]

    identificador_unico = models.CharField(max_length=50, unique=True, editable=False)
    nombre_descriptivo = models.CharField(max_length=150)
    dia_semana = models.SmallIntegerField(
        choices=DIAS_SEMANA,
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    activa = models.BooleanField(default=True)
    cedis = models.ForeignKey(
        Cedis, 
        on_delete=models.RESTRICT,
        related_name='rutas'
    )
    clientes = models.ManyToManyField(
        Cliente,
        through='RutaCliente',
        related_name='rutas'
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'rutas'
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'
        ordering = ['dia_semana', 'nombre_descriptivo']
        indexes = [
            models.Index(fields=['dia_semana', 'cedis']),
            models.Index(fields=['activa']),
        ]

    def __str__(self):
        return f"{self.identificador_unico} - {self.nombre_descriptivo}"

    def save(self, *args, **kwargs):
        """
        Genera automáticamente el identificador único al crear la ruta
        """
        if not self.identificador_unico:
            self.identificador_unico = self._generar_identificador()
        super().save(*args, **kwargs)

    def _generar_identificador(self):
        """
        Genera un identificador único para la ruta
        Formato: RUT-{CEDIS_ID}-{DIA}-{UUID_CORTO}
        """
        uuid_corto = str(uuid.uuid4())[:8].upper()
        return f"RUT-{self.cedis.id}-{self.dia_semana}-{uuid_corto}"

    @property
    def total_clientes(self):
        """Retorna el número total de clientes en la ruta"""
        return self.clientes.count()

    def puede_eliminarse(self):
        """
        Verifica si la ruta puede ser eliminada
        Cumple con RF-RUT-03: No se puede eliminar si tiene asignaciones activas
        """
        from django.utils import timezone
        return not self.asignaciones.filter(
            fecha__gte=timezone.now().date()
        ).exists()


class RutaCliente(models.Model):
    """
    Modelo de asociación entre Rutas y Clientes
    Responsabilidad: Gestionar el orden de visita de clientes en una ruta
    """
    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        related_name='ruta_clientes'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.RESTRICT,
        related_name='cliente_rutas'
    )
    orden_visita = models.IntegerField()

    class Meta:
        db_table = 'rutas_clientes'
        verbose_name = 'Cliente en Ruta'
        verbose_name_plural = 'Clientes en Rutas'
        ordering = ['ruta', 'orden_visita']
        unique_together = [
            ('ruta', 'cliente'),
            ('ruta', 'orden_visita'),
        ]
        indexes = [
            models.Index(fields=['ruta', 'orden_visita']),
        ]

    def __str__(self):
        return f"{self.ruta.identificador_unico} - {self.cliente.nombre_comercial} (Orden: {self.orden_visita})"


class AsignacionRuta(models.Model):
    """
    Modelo para asignación de rutas a vendedores
    Responsabilidad: Gestionar las asignaciones diarias de rutas a vendedores
    """
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Progreso', 'En Progreso'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]

    fecha = models.DateField()
    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.RESTRICT,
        related_name='asignaciones'
    )
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.RESTRICT,
        related_name='asignaciones'
    )
    estado = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default='Pendiente'
    )

    class Meta:
        db_table = 'asignaciones_rutas'
        verbose_name = 'Asignación de Ruta'
        verbose_name_plural = 'Asignaciones de Rutas'
        ordering = ['-fecha', 'ruta']
        unique_together = [('fecha', 'ruta')]
        indexes = [
            models.Index(fields=['fecha', 'vendedor']),
            models.Index(fields=['fecha', 'ruta']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.ruta.identificador_unico} - {self.vendedor.nombre_completo} ({self.fecha})"
