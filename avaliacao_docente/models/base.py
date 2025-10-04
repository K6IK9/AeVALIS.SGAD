"""
Classe base abstrata para todos os models do sistema.
Implementa comportamento padrão e métodos utilitários.
"""

from django.db import models


class BaseModel(models.Model):
    """
    Classe base abstrata para todos os models do sistema.

    Fornece implementações padrão de:
    - __repr__: Representação para debug
    - clean: Validação customizada (pode ser sobrescrita)
    - delete: Suporte a soft delete (se modelo tiver campo 'ativo')
    - save: Validação automática via full_clean()

    Todos os models concretos devem herdar desta classe para
    garantir comportamento consistente.
    """

    class Meta:
        abstract = True

    def __repr__(self):
        """
        Representação string para debug.
        Exemplo: <Turma: ALG-2024.1-MAT>
        """
        return f"<{self.__class__.__name__}: {self}>"

    def clean(self):
        """
        Validação customizada do modelo.
        Sobrescreva este método para adicionar validações específicas.
        Sempre chame super().clean() na implementação.
        """
        super().clean()

    def delete(self, using=None, keep_parents=False):
        """
        Implementa soft delete se o modelo tiver campo 'ativo'.

        Para modelos com SoftDeleteMixin:
            - Marca ativo=False ao invés de deletar
            - Use .soft_delete() para soft delete explícito
            - Use .delete(force=True) para hard delete

        Para modelos sem soft delete:
            - Executa delete normal do Django
        """
        if hasattr(self, "ativo"):
            # Soft delete: marca como inativo
            from django.utils import timezone

            self.ativo = False
            if hasattr(self, "data_exclusao"):
                self.data_exclusao = timezone.now()
            self.save(using=using)
        else:
            # Hard delete: remove do banco de dados
            super().delete(using=using, keep_parents=keep_parents)

    def hard_delete(self, using=None, keep_parents=False):
        """
        Força exclusão física do banco de dados (hard delete).
        Use com cautela - não há como recuperar.
        """
        super().delete(using=using, keep_parents=keep_parents)

    def save(self, *args, **kwargs):
        """
        Salva o modelo após executar validações.

        Chama self.full_clean() automaticamente antes de salvar,
        garantindo que todas as validações sejam executadas.

        Para pular validação (não recomendado), passe skip_validation=True:
            obj.save(skip_validation=True)
        """
        skip_validation = kwargs.pop("skip_validation", False)

        if not skip_validation:
            self.full_clean()

        super().save(*args, **kwargs)
