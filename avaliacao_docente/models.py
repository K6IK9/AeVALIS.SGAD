from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class PerfilProfessorManager(models.Manager):
    """Manager customizado para excluir usuários admin"""

    def get_queryset(self):
        from rolepermissions.checkers import has_role

        # Obter IDs de admins de forma lazy
        try:
            admin_ids = [
                user.id for user in User.objects.all() if has_role(user, "admin")
            ]
        except Exception:
            # Se houver erro (tabelas não existem), retorna queryset vazio de exclusão
            admin_ids = []

        return super().get_queryset().exclude(user__id__in=admin_ids)

    def non_admin(self):
        """Retorna apenas professores que não são admin"""
        return self.get_queryset()


class PerfilAlunoManager(models.Manager):
    """Manager customizado para excluir usuários admin"""

    def get_queryset(self):
        from rolepermissions.checkers import has_role

        # Obter IDs de admins de forma lazy
        try:
            admin_ids = [
                user.id for user in User.objects.all() if has_role(user, "admin")
            ]
        except Exception:
            # Se houver erro (tabelas não existem), retorna queryset vazio de exclusão
            admin_ids = []

        return super().get_queryset().exclude(user__id__in=admin_ids)

    def non_admin(self):
        """Retorna apenas alunos que não são admin"""
        return self.get_queryset()


class PerfilAluno(models.Model):
    """
    Extensão do modelo User para dados específicos de alunos
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil_aluno"
    )
    situacao = models.CharField(max_length=45, default="Ativo")

    objects = models.Manager()  # Manager padrão
    non_admin = PerfilAlunoManager()  # Manager que exclui admins

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.username}"

    @property
    def matricula(self):
        return self.user.username

    @property
    def nome_completo(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def email(self):
        return self.user.email


class PerfilProfessor(models.Model):
    """
    Extensão do modelo User para dados específicos de professores
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil_professor"
    )
    registro_academico = models.CharField(max_length=45)

    objects = models.Manager()  # Manager padrão
    non_admin = PerfilProfessorManager()  # Manager que exclui admins

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registro_academico})"


class Curso(models.Model):
    curso_nome = models.CharField(max_length=45)
    curso_sigla = models.CharField(max_length=10)
    coordenador_curso = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="cursos"
    )

    def __str__(self):
        return f"{self.curso_nome} ({self.curso_sigla})"


class PeriodoLetivo(models.Model):
    SEMESTRE_CHOICES = [
        (1, "1º Semestre"),
        (2, "2º Semestre"),
        (3, "3º Semestre"),
        (4, "4º Semestre"),
        (5, "5º Semestre"),
        (6, "6º Semestre"),
        (7, "7º Semestre"),
        (8, "8º Semestre"),
        (9, "9º Semestre"),
        (10, "10º Semestre"),
    ]

    nome = models.CharField(max_length=50)
    ano = models.IntegerField()
    semestre = models.IntegerField(choices=SEMESTRE_CHOICES)

    class Meta:
        unique_together = ["ano", "semestre"]
        ordering = ["-ano", "-semestre"]

    def __str__(self):
        return f"{self.nome} - {self.ano}.{self.semestre}"


class Disciplina(models.Model):
    TIPO_CHOICES = [
        ("Obrigatória", "Obrigatória"),
        ("Optativa", "Optativa"),
    ]

    disciplina_nome = models.CharField(max_length=100)
    disciplina_sigla = models.CharField(max_length=45)
    disciplina_tipo = models.CharField(max_length=45, choices=TIPO_CHOICES)
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="disciplinas"
    )
    professor = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="disciplinas"
    )
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo, on_delete=models.CASCADE, related_name="disciplinas"
    )

    def __str__(self):
        return f"{self.disciplina_nome} ({self.disciplina_sigla})"


class Turma(models.Model):
    """
    Modelo principal para gerenciar turmas
    """

    TURNO_CHOICES = [
        ("matutino", "Matutino"),
        ("vespertino", "Vespertino"),
        ("noturno", "Noturno"),
    ]

    STATUS_CHOICES = [
        ("ativa", "Ativa"),
        ("finalizada", "Finalizada"),
    ]

    codigo_turma = models.CharField(max_length=100, unique=True)  # Ex: "INFO3A-2024.1"
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name="turmas"
    )
    professor = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="turmas"
    )
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo, on_delete=models.CASCADE, related_name="turmas"
    )

    turno = models.CharField(max_length=15, choices=TURNO_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="ativa")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["disciplina", "periodo_letivo", "turno"]
        ordering = ["periodo_letivo", "disciplina__disciplina_nome"]

    def save(self, *args, **kwargs):
        # Auto-gera código da turma se não existir
        if not self.codigo_turma:
            # Usa sigla da disciplina (max 10 chars) + ano + semestre + turno abreviado
            sigla = self.disciplina.disciplina_sigla[:10]  # Limita sigla a 10 chars
            ano = str(self.periodo_letivo.ano)
            semestre = str(self.periodo_letivo.semestre)
            turno_map = {"matutino": "M", "vespertino": "V", "noturno": "N"}
            turno_abrev = turno_map.get(self.turno, self.turno[:1].upper())

            self.codigo_turma = f"{sigla}-{ano}.{semestre}{turno_abrev}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_turma} - {self.disciplina.disciplina_nome}"

    def count_alunos_matriculados(self):
        """
        Conta apenas alunos matriculados (exclui admins)
        """
        from rolepermissions.checkers import has_role

        count = 0
        for matricula in self.matriculas.filter(status="ativa"):
            if not has_role(matricula.aluno.user, "admin"):
                count += 1
        return count


class MatriculaTurma(models.Model):
    """
    Relacionamento entre alunos e turmas (matrícula)
    """

    STATUS_MATRICULA_CHOICES = [
        ("ativa", "Ativa"),
        ("trancada", "Trancada"),
        ("cancelada", "Cancelada"),
        ("concluida", "Concluída"),
    ]

    aluno = models.ForeignKey(
        PerfilAluno, on_delete=models.CASCADE, related_name="matriculas"
    )
    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE, related_name="matriculas"
    )

    data_matricula = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=15, choices=STATUS_MATRICULA_CHOICES, default="ativa"
    )

    class Meta:
        unique_together = ["aluno", "turma"]
        ordering = ["data_matricula"]

    def __str__(self):
        return f"{self.aluno.user.get_full_name()} em {self.turma.codigo_turma}"


class HorarioTurma(models.Model):
    """
    Horários das aulas da turma
    """

    DIAS_SEMANA_CHOICES = [
        (1, "Segunda-feira"),
        (2, "Terça-feira"),
        (3, "Quarta-feira"),
        (4, "Quinta-feira"),
        (5, "Sexta-feira"),
        (6, "Sábado"),
    ]

    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="horarios")
    dia_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        unique_together = ["turma", "dia_semana", "hora_inicio"]
        ordering = ["dia_semana", "hora_inicio"]

    def __str__(self):
        return f"{self.turma.codigo_turma} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fim}"


# ============ NOVO SISTEMA DE AVALIAÇÃO DOCENTE ============


class QuestionarioAvaliacao(models.Model):
    """
    Template de questionário que pode ser reutilizado para diferentes avaliações
    """

    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="questionarios_criados"
    )

    class Meta:
        ordering = ["-data_criacao"]
        verbose_name = "Questionário de Avaliação"
        verbose_name_plural = "Questionários de Avaliação"

    def __str__(self):
        return self.titulo


class CategoriaPergunta(models.Model):
    """
    Categorias para organizar as perguntas (ex: Didática, Relacionamento, Infraestrutura)
    """

    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Categoria de Pergunta"
        verbose_name_plural = "Categorias de Perguntas"

    def __str__(self):
        return self.nome


class PerguntaAvaliacao(models.Model):
    """
    Modelo aprimorado para perguntas da avaliação
    """

    TIPO_CHOICES = [
        (
            "likert",
            "Escala de Concordância (Likert) - Discordo totalmente / Concordo totalmente",
        ),
        ("nps", "Net Promoter Score - Escala 0 a 10 para recomendação"),
        ("multipla_escolha", "Múltipla Escolha - Uma ou mais opções"),
        ("sim_nao", "Sim ou Não - Resposta binária simples"),
        ("texto_livre", "Resposta Aberta - Comentários livres e sugestões"),
    ]

    enunciado = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(
        CategoriaPergunta, on_delete=models.CASCADE, related_name="perguntas"
    )
    obrigatoria = models.BooleanField(default=True)
    ativa = models.BooleanField(default=True)

    # Para perguntas de múltipla escolha
    opcoes_multipla_escolha = models.JSONField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["categoria__ordem"]
        verbose_name = "Pergunta de Avaliação"
        verbose_name_plural = "Perguntas de Avaliação"

    def __str__(self):
        return f"{self.categoria.nome}: {self.enunciado[:50]}..."


class QuestionarioPergunta(models.Model):
    """
    Relacionamento entre questionários e perguntas
    """

    questionario = models.ForeignKey(
        QuestionarioAvaliacao, on_delete=models.CASCADE, related_name="perguntas"
    )
    pergunta = models.ForeignKey(
        PerguntaAvaliacao, on_delete=models.CASCADE, related_name="questionarios"
    )
    ordem_no_questionario = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["questionario", "pergunta"]
        ordering = ["ordem_no_questionario"]
        verbose_name = "Pergunta do Questionário"
        verbose_name_plural = "Perguntas do Questionário"

    def __str__(self):
        return f"{self.questionario.titulo} - {self.pergunta.enunciado[:30]}..."


class CicloAvaliacao(models.Model):
    """
    Representa um período/ciclo de avaliação institucional
    """

    nome = models.CharField(max_length=100)  # Ex: "Avaliação Docente 2024.1"
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo, on_delete=models.CASCADE, related_name="ciclos_avaliacao"
    )
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    questionario = models.ForeignKey(
        QuestionarioAvaliacao, on_delete=models.CASCADE, related_name="ciclos"
    )
    ativo = models.BooleanField(default=True)

    # Configurações do ciclo
    permite_avaliacao_anonima = models.BooleanField(default=True)
    permite_multiplas_respostas = models.BooleanField(default=False)
    enviar_lembrete_email = models.BooleanField(default=True)

    # Turmas que devem responder a avaliação
    turmas = models.ManyToManyField(
        Turma,
        related_name="ciclos_avaliacao",
        blank=True,
        verbose_name="Turmas que devem responder",
        help_text="Selecione as turmas que devem participar desta avaliação",
    )

    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ciclos_criados"
    )

    class Meta:
        ordering = ["-data_inicio"]
        verbose_name = "Ciclo de Avaliação"
        verbose_name_plural = "Ciclos de Avaliação"

    def __str__(self):
        return f"{self.nome} ({self.periodo_letivo})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Garante que o questionário vinculado possui perguntas
        if self.questionario_id:
            try:
                has_perguntas = self.questionario.perguntas.exists()
            except Exception:
                # Em fases iniciais (migrações) não validar
                has_perguntas = True

            if not has_perguntas:
                raise ValidationError(
                    {
                        "questionario": "O questionário selecionado não possui perguntas cadastradas."
                    }
                )

    def save(self, *args, **kwargs):
        # Executa validações de modelo antes de salvar
        from django.core.exceptions import ValidationError

        try:
            self.full_clean()
        except ValidationError:
            # Repropaga para o chamador (FormView capturará e exibirá)
            raise
        return super().save(*args, **kwargs)

    @property
    def status(self):
        from django.utils import timezone

        now = timezone.now()

        if now < self.data_inicio:
            return "agendado"
        elif now > self.data_fim:
            return "finalizado"
        else:
            return "em_andamento"

    def total_avaliacoes_previstas(self):
        """Calcula quantas avaliações deveriam ser feitas"""
        total = 0
        for avaliacao in self.avaliacoes.all():
            total += avaliacao.turma.count_alunos_matriculados()
        return total

    def total_avaliacoes_respondidas(self):
        """Conta quantas avaliações foram efetivamente respondidas"""
        return self.avaliacoes.filter(respostas__isnull=False).distinct().count()

    def percentual_participacao(self):
        """Calcula o percentual de participação na avaliação"""
        previstas = self.total_avaliacoes_previstas()
        if previstas == 0:
            return 0
        respondidas = self.total_avaliacoes_respondidas()
        return round((respondidas / previstas) * 100, 2)


class AvaliacaoDocente(models.Model):
    """
    Representa uma avaliação específica de um professor/disciplina em uma turma
    """

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_andamento", "Em Andamento"),
        ("finalizada", "Finalizada"),
        ("cancelada", "Cancelada"),
    ]

    ciclo = models.ForeignKey(
        CicloAvaliacao, on_delete=models.CASCADE, related_name="avaliacoes"
    )
    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE, related_name="avaliacoes_docente"
    )
    professor = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="avaliacoes_recebidas"
    )
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name="avaliacoes_docente"
    )

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pendente")

    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["ciclo", "turma", "professor", "disciplina"]
        ordering = ["-data_criacao"]
        verbose_name = "Avaliação Docente"
        verbose_name_plural = "Avaliações Docentes"

    def __str__(self):
        return f"Avaliação {self.professor} - {self.disciplina.disciplina_nome} ({self.turma.codigo_turma})"

    def total_respostas(self):
        """Conta o total de alunos que responderam esta avaliação"""
        return self.respostas.values("aluno").distinct().count()

    def alunos_aptos(self):
        """Retorna alunos matriculados na turma que podem avaliar"""
        from rolepermissions.checkers import has_role

        alunos_matriculados = []
        for matricula in self.turma.matriculas.filter(status="ativa"):
            if not has_role(matricula.aluno.user, "admin"):
                alunos_matriculados.append(matricula.aluno)
        return alunos_matriculados

    def percentual_participacao(self):
        """Calcula percentual de participação nesta avaliação específica"""
        total_alunos = len(self.alunos_aptos())
        if total_alunos == 0:
            return 0

        total_respostas = self.total_respostas()
        return round((total_respostas / total_alunos) * 100, 2)

    def media_geral(self):
        """Calcula a média geral das respostas numéricas"""
        from django.db.models import Avg

        # Considera apenas perguntas de escala (likert e nps)
        respostas_numericas = self.respostas.filter(
            pergunta__tipo__in=["likert", "nps"]
        )

        if not respostas_numericas.exists():
            return None

        # Converte respostas para valores numéricos e calcula média
        total = 0
        count = 0

        for resposta in respostas_numericas:
            try:
                valor = float(resposta.valor_numerico or resposta.valor_texto)
                total += valor
                count += 1
            except (ValueError, TypeError):
                continue

        return round(total / count, 2) if count > 0 else None

    def get_media_por_categoria(self):
        """Retorna a média por categoria de pergunta"""
        from django.db.models import Avg

        categorias = {}
        for categoria in CategoriaPergunta.objects.filter(ativa=True):
            respostas = self.respostas.filter(
                pergunta__categoria=categoria, pergunta__tipo__in=["likert", "nps"]
            )

            if respostas.exists():
                total = 0
                count = 0
                for resposta in respostas:
                    try:
                        valor = float(resposta.valor_numerico or resposta.valor_texto)
                        total += valor
                        count += 1
                    except (ValueError, TypeError):
                        continue

                if count > 0:
                    categorias[categoria.nome] = round(total / count, 2)

        return categorias


class RespostaAvaliacao(models.Model):
    """
    Resposta de um aluno a uma pergunta específica de uma avaliação
    """

    avaliacao = models.ForeignKey(
        AvaliacaoDocente, on_delete=models.CASCADE, related_name="respostas"
    )
    aluno = models.ForeignKey(
        PerfilAluno,
        on_delete=models.CASCADE,
        related_name="respostas_avaliacoes",
        null=True,  # Permite respostas anônimas
        blank=True,
    )
    pergunta = models.ForeignKey(
        PerguntaAvaliacao, on_delete=models.CASCADE, related_name="respostas"
    )

    # Diferentes tipos de resposta
    valor_texto = models.TextField(blank=True)
    valor_numerico = models.IntegerField(null=True, blank=True)  # Para escalas
    valor_boolean = models.BooleanField(null=True, blank=True)  # Para sim/não

    # Metadados
    data_resposta = models.DateTimeField(auto_now_add=True)
    anonima = models.BooleanField(default=False)

    # Para controle de sessão anônima
    session_key = models.CharField(max_length=40, blank=True)

    class Meta:
        unique_together = ["avaliacao", "aluno", "pergunta", "session_key"]
        ordering = ["data_resposta"]
        verbose_name = "Resposta de Avaliação"
        verbose_name_plural = "Respostas de Avaliação"

    def __str__(self):
        identificacao = (
            f"Anônimo ({self.session_key[:8]})" if self.anonima else str(self.aluno)
        )
        return f"{identificacao} - {self.pergunta.enunciado[:30]}..."

    def valor_display(self):
        """Retorna o valor da resposta formatado para exibição"""
        if self.valor_numerico is not None:
            if self.pergunta.tipo == "likert":
                # Escala Likert de 1 a 5
                escalas = {
                    1: "Discordo totalmente",
                    2: "Discordo parcialmente",
                    3: "Neutro",
                    4: "Concordo parcialmente",
                    5: "Concordo totalmente",
                }
                return (
                    f"{self.valor_numerico} - {escalas.get(self.valor_numerico, 'N/A')}"
                )
            elif self.pergunta.tipo == "nps":
                # NPS de 0 a 10
                return f"{self.valor_numerico}/10"
            return str(self.valor_numerico)
        elif self.valor_boolean is not None:
            return "Sim" if self.valor_boolean else "Não"
        else:
            return self.valor_texto or "Sem resposta"


class ConfiguracaoSite(models.Model):
    """Modelo para armazenar configurações globais do site. Singleton."""
    METODO_CHOICES = (
        ('api', 'API (Recomendado para Vercel)'),
        ('smtp', 'SMTP (Para desenvolvimento local/outros hosts)'),
    )
    metodo_envio_email = models.CharField(
        max_length=10,
        choices=METODO_CHOICES,
        default='api',
        help_text="Escolha o método para enviar e-mails. 'API' é necessário para a Vercel."
    )
    email_notificacao_erros = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        help_text="E-mail para receber notificações de erros do sistema (quando DEBUG=False)."
    )

    def save(self, *args, **kwargs):
        """Garante que apenas uma instância deste modelo exista."""
        if not self.pk and ConfiguracaoSite.objects.exists():
            # Impede a criação de uma nova instância se uma já existir
            raise ValidationError('Só pode haver uma instância de Configuração do Site.')
        return super(ConfiguracaoSite, self).save(*args, **kwargs)

    @classmethod
    def obter_config(cls):
        """Obtém a instância de configuração única, criando-a se não existir."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# ============ MODELOS DEPRECATED (MANTER COMPATIBILIDADE) ============

# As definições dos modelos abaixo foram removidas em [data da remoção].
# Eles foram substituídos pelo novo sistema de avaliação (AvaliacaoDocente, etc.)
# e mantidos aqui apenas como um comentário histórico.

