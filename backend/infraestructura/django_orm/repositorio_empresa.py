"""
Repositorio de Empresa - Implementación con Django ORM
Capa de Infraestructura
"""
from typing import List, Optional
from aplicacion.interfaces.repositorios import IRepositorioEmpresa
from dominio.entidades.empresa import Empresa
from infraestructura.django_orm.models import EmpresaModel


class RepositorioEmpresaDjango(IRepositorioEmpresa):
    """Implementación del repositorio de Empresa usando Django ORM"""
    
    def guardar(self, empresa: Empresa) -> Empresa:
        """Persiste una empresa en la BD"""
        empresa_model = EmpresaModel(
            nombre=empresa.nombre,
            nit=empresa.nit,
            direccion=empresa.direccion,
            telefono=empresa.telefono,
            email=empresa.email,
            activo=empresa.activo
        )
        empresa_model.save()
        empresa.id = empresa_model.id
        return empresa
    
    def obtener_por_id(self, empresa_id: int) -> Optional[Empresa]:
        """Obtiene una empresa por ID"""
        try:
            modelo = EmpresaModel.objects.get(id=empresa_id)
            return self._modelo_a_entidad(modelo)
        except EmpresaModel.DoesNotExist:
            return None
    
    def obtener_por_nit(self, nit: str) -> Optional[Empresa]:
        """Obtiene una empresa por NIT"""
        try:
            modelo = EmpresaModel.objects.get(nit=nit)
            return self._modelo_a_entidad(modelo)
        except EmpresaModel.DoesNotExist:
            return None
    
    def listar_activas(self) -> List[Empresa]:
        """Lista todas las empresas activas"""
        modelos = EmpresaModel.objects.filter(activo=True)
        return [self._modelo_a_entidad(m) for m in modelos]
    
    def listar_todas(self) -> List[Empresa]:
        """Lista todas las empresas"""
        modelos = EmpresaModel.objects.all()
        return [self._modelo_a_entidad(m) for m in modelos]
    
    def existe_nit(self, nit: str, excluir_id: Optional[int] = None) -> bool:
        """Verifica si existe un NIT"""
        queryset = EmpresaModel.objects.filter(nit=nit)
        if excluir_id:
            queryset = queryset.exclude(id=excluir_id)
        return queryset.exists()
    
    def actualizar(self, empresa: Empresa) -> Empresa:
        """Actualiza una empresa"""
        modelo = EmpresaModel.objects.get(id=empresa.id)
        modelo.nombre = empresa.nombre
        modelo.nit = empresa.nit
        modelo.direccion = empresa.direccion
        modelo.telefono = empresa.telefono
        modelo.email = empresa.email
        modelo.activo = empresa.activo
        modelo.save()
        return empresa
    
    def eliminar(self, empresa_id: int) -> bool:
        """Elimina (soft delete) una empresa"""
        try:
            modelo = EmpresaModel.objects.get(id=empresa_id)
            modelo.activo = False
            modelo.save()
            return True
        except EmpresaModel.DoesNotExist:
            return False
    
    def _modelo_a_entidad(self, modelo: EmpresaModel) -> Empresa:
        """Convierte un modelo Django a entidad de dominio"""
        return Empresa(
            id=modelo.id,
            nombre=modelo.nombre,
            nit=modelo.nit,
            direccion=modelo.direccion,
            telefono=modelo.telefono,
            email=modelo.email,
            activo=modelo.activo,
            fecha_creacion=modelo.fecha_creacion,
            fecha_actualizacion=modelo.fecha_actualizacion
        )
