"""
Custom managers para models com soft delete e outras funcionalidades.

Managers definem como queries são executadas por padrão.
"""

from django.db import models


class SoftDeleteManager(models.Manager):
    """
    Manager que filtra automaticamente registros inativos.

    Por padrão, todas as queries retornam apenas registros com ativo=True.
    Use métodos adicionais para acessar registros deletados.

    Métodos:
        - get_queryset(): Filtrado (apenas ativos)
        - all_with_deleted(): Todos os registros
        - deleted_only(): Apenas registros deletados

    Uso:
        class MeuModel(BaseModel, SoftDeleteMixin):
            nome = models.CharField(max_length=100)

            objects = SoftDeleteManager()  # Manager padrão (filtrado)
            all_objects = models.Manager()  # Manager sem filtro

        # Queries:
        MeuModel.objects.all()  # Apenas ativos
        MeuModel.objects.deleted_only()  # Apenas deletados
        MeuModel.all_objects.all()  # Todos (ativos + deletados)
    """

    def get_queryset(self):
        """
        Retorna queryset filtrado para registros ativos.

        Sobrescreve get_queryset() para adicionar filtro ativo=True
        automaticamente em todas as queries.
        """
        return super().get_queryset().filter(ativo=True)

    def all_with_deleted(self):
        """
        Retorna todos os registros, incluindo os deletados (ativo=False).

        Use quando precisar acessar registros deletados para
        relatórios, auditoria ou recuperação.

        Retorna:
            QuerySet: Todos os registros sem filtro

        Exemplo:
            todas_turmas = Turma.objects.all_with_deleted()
            print(f"Total (com deletadas): {todas_turmas.count()}")
        """
        return super().get_queryset()

    def deleted_only(self):
        """
        Retorna apenas registros deletados (ativo=False).

        Útil para listar itens na "lixeira" ou para recuperação.

        Retorna:
            QuerySet: Apenas registros com ativo=False

        Exemplo:
            turmas_deletadas = Turma.objects.deleted_only()
            for turma in turmas_deletadas:
                print(f"Deletada em: {turma.data_exclusao}")
        """
        return super().get_queryset().filter(ativo=False)

    def restore(self, pk):
        """
        Restaura um registro deletado pelo ID.

        Args:
            pk: Primary key do registro a restaurar

        Retorna:
            Model instance: Registro restaurado

        Raises:
            DoesNotExist: Se registro não existir

        Exemplo:
            turma = Turma.objects.restore(pk=123)
            print(f"Turma {turma} restaurada!")
        """
        obj = self.all_with_deleted().get(pk=pk)
        obj.restore()
        return obj


class ActiveManager(models.Manager):
    """
    Manager alternativo que filtra por ativo=True.

    Similar ao SoftDeleteManager, mas não fornece métodos adicionais.
    Use quando quiser um manager simples apenas para filtrar ativos.

    Uso:
        class MeuModel(models.Model):
            ativo = models.BooleanField(default=True)

            objects = models.Manager()  # Todos
            ativos = ActiveManager()  # Apenas ativos

        MeuModel.objects.all()  # Todos
        MeuModel.ativos.all()  # Apenas ativos
    """

    def get_queryset(self):
        """Retorna apenas registros ativos."""
        return super().get_queryset().filter(ativo=True)
