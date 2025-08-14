from django import forms
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from .models import (
    Curso,
    PerfilProfessor,
    Disciplina,
    PeriodoLetivo,
    Turma,
    PerfilAluno,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    CicloAvaliacao,
    RespostaAvaliacao,
    ComentarioAvaliacao,
)


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nome",
        widget=forms.TextInput(attrs={"placeholder": "Nome"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Sobrenome",
        widget=forms.TextInput(attrs={"placeholder": "Sobrenome"}),
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        label="Email Institucional",
        widget=forms.EmailInput(attrs={"placeholder": "Email institucional"}),
    )
    username = forms.CharField(
        required=True,
        label="Matrícula",
        widget=forms.TextInput(attrs={"placeholder": "Matrícula"}),
    )
    password1 = forms.CharField(
        required=True,
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Senha"}),
    )
    password2 = forms.CharField(
        required=True,
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirme a senha"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Verifica se o email já existe
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Este email já está sendo usado por outro usuário."
                )

        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Validação para formato de matrícula (opcional - pode ser personalizada)
            if not username.isdigit():
                raise forms.ValidationError("A matrícula deve conter apenas números.")
            if len(username) < 6:
                raise forms.ValidationError(
                    "A matrícula deve ter pelo menos 6 dígitos."
                )

        return username


class GerenciarRoleForm(forms.Form):
    """
    Form para gerenciar permissões de usuários
    """

    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Usuário",
    )

    role = forms.ChoiceField(
        choices=[
            ("aluno", "Aluno"),
            ("professor", "Professor"),
            ("coordenador", "Coordenador"),
            ("admin", "Administrador"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Role",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordena usuários por username
        self.fields["usuario"].queryset = User.objects.all().order_by("username")


class GerenciarUsuarioForm(forms.ModelForm):
    """
    Form para criar e editar usuários
    """

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nome",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite o nome"}
        ),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Sobrenome",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite o sobrenome"}
        ),
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        label="Email Institucional",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite o email institucional",
            }
        ),
    )
    username = forms.CharField(
        required=True,
        label="Matrícula",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite a matrícula"}
        ),
    )
    is_active = forms.BooleanField(
        required=False,
        label="Usuário Ativo",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        initial=True,
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Verifica se o email já existe (exceto para o próprio usuário em edição)
            queryset = User.objects.filter(email=email)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(
                    "Este email já está sendo usado por outro usuário."
                )
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Validação para formato de matrícula
            if not username.isdigit():
                raise forms.ValidationError("A matrícula deve conter apenas números.")
            if len(username) < 6:
                raise forms.ValidationError(
                    "A matrícula deve ter pelo menos 6 dígitos."
                )
            # Verifica se a matrícula já existe (exceto para o próprio usuário em edição)
            queryset = User.objects.filter(username=username)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(
                    "Esta matrícula já está sendo usada por outro usuário."
                )
        return username


class CursoForm(forms.ModelForm):
    """
    Form para criação e edição de cursos
    """

    curso_nome = forms.CharField(
        max_length=45,
        required=True,
        label="Nome do Curso",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite o nome do curso"}
        ),
    )
    curso_sigla = forms.CharField(
        max_length=10,
        required=True,
        label="Sigla do Curso",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite a sigla do curso"}
        ),
    )
    coordenador_curso = forms.ModelChoiceField(
        queryset=PerfilProfessor.non_admin.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Coordenador do Curso",
    )

    class Meta:
        model = Curso
        fields = ["curso_nome", "curso_sigla", "coordenador_curso"]

    def clean_curso_nome(self):
        curso_nome = self.cleaned_data.get("curso_nome")
        if curso_nome:
            # Verifica se o curso já existe
            if Curso.objects.filter(curso_nome__iexact=curso_nome).exists():
                raise forms.ValidationError("Este curso já existe no sistema.")
        return curso_nome


class DisciplinaForm(forms.ModelForm):
    """
    Form para criação e edição de disciplinas
    """

    disciplina_nome = forms.CharField(
        max_length=100,
        required=True,
        label="Nome da Disciplina",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite o nome da disciplina",
            }
        ),
    )
    disciplina_sigla = forms.CharField(
        max_length=45,
        required=True,
        label="Sigla da Disciplina",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite a sigla da disciplina",
            }
        ),
    )
    disciplina_tipo = forms.ChoiceField(
        required=True,
        label="Tipo da Disciplina",
        choices=Disciplina.TIPO_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-control"},
        ),
    )
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Curso",
    )
    professor = forms.ModelChoiceField(
        queryset=PerfilProfessor.non_admin.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Professor Responsável",
    )
    periodo_letivo = forms.ModelChoiceField(
        queryset=PeriodoLetivo.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Período Letivo",
        required=True,
    )

    class Meta:
        model = Disciplina
        fields = [
            "disciplina_nome",
            "disciplina_sigla",
            "disciplina_tipo",
            "curso",
            "professor",
            "periodo_letivo",
        ]

    def clean_disciplina_nome(self):
        disciplina_nome = self.cleaned_data.get("disciplina_nome")
        curso = self.cleaned_data.get("curso")
        if disciplina_nome and curso:
            # Verifica se a disciplina já existe no mesmo curso
            if Disciplina.objects.filter(
                disciplina_nome__iexact=disciplina_nome, curso=curso
            ).exists():
                raise forms.ValidationError("Esta disciplina já existe neste curso.")
        return disciplina_nome


class PeriodoLetivoForm(forms.ModelForm):

    nome = forms.CharField(
        max_length=50,
        required=True,
        label="Nome do Período",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ex: Período Letivo 2024.1"}
        ),
    )
    ano = forms.IntegerField(
        required=True,
        label="Ano",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "2024",
                "min": "2020",
                "max": "2030",
            }
        ),
    )
    semestre = forms.ChoiceField(
        required=True,
        label="Semestre",
        choices=PeriodoLetivo.SEMESTRE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = PeriodoLetivo
        fields = ["nome", "ano", "semestre"]

    def clean(self):
        cleaned_data = super().clean()
        ano = cleaned_data.get("ano")
        semestre = cleaned_data.get("semestre")

        if ano and semestre:
            # Verifica se já existe um período para o mesmo ano e semestre
            if PeriodoLetivo.objects.filter(ano=ano, semestre=semestre).exists():
                raise forms.ValidationError(
                    f"Já existe um período cadastrado para {ano}.{semestre}"
                )

        return cleaned_data


class TurmaForm(forms.ModelForm):
    """
    Form para criação e edição de turmas
    """

    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Disciplina",
    )
    professor = forms.ModelChoiceField(
        queryset=PerfilProfessor.non_admin.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Professor",
    )
    periodo_letivo = forms.ModelChoiceField(
        queryset=PeriodoLetivo.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Período Letivo",
    )
    turno = forms.ChoiceField(
        choices=[("", "--- Selecione ---")] + Turma.TURNO_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Turno",
    )

    class Meta:
        model = Turma
        fields = [
            "disciplina",
            "professor",
            "periodo_letivo",
            "turno",
        ]

    def clean(self):
        cleaned_data = super().clean()
        disciplina = cleaned_data.get("disciplina")
        periodo_letivo = cleaned_data.get("periodo_letivo")
        turno = cleaned_data.get("turno")

        if disciplina and periodo_letivo and turno:
            # Verifica se já existe uma turma para essa disciplina no mesmo período e turno
            if Turma.objects.filter(
                disciplina=disciplina,
                periodo_letivo=periodo_letivo,
                turno=turno,
            ).exists():
                raise forms.ValidationError(
                    f"Já existe uma turma de {disciplina.disciplina_nome} "
                    f"no período {periodo_letivo} no turno {turno}."
                )

        return cleaned_data


# ============ FORMS PARA NOVO SISTEMA DE AVALIAÇÃO ============


class CicloAvaliacaoForm(forms.ModelForm):
    """
    Formulário para criar/editar ciclos de avaliação
    """

    turmas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="Turmas que devem responder",
        help_text="Selecione as turmas que devem participar desta avaliação",
    )

    class Meta:
        model = CicloAvaliacao
        fields = [
            "nome",
            "periodo_letivo",
            "questionario",
            "data_inicio",
            "data_fim",
            "turmas",
            "permite_avaliacao_anonima",
            "permite_multiplas_respostas",
            "enviar_lembrete_email",
        ]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Avaliação Docente 2024.1",
                }
            ),
            "periodo_letivo": forms.Select(attrs={"class": "form-control"}),
            "questionario": forms.Select(attrs={"class": "form-control"}),
            "data_inicio": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "data_fim": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "permite_avaliacao_anonima": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "permite_multiplas_respostas": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "enviar_lembrete_email": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar turmas apenas do período letivo selecionado
        # Para novas instâncias, sempre mostrar todas as turmas ativas
        # Filtrar questionários para exibir apenas aqueles com perguntas
        try:
            self.fields["questionario"].queryset = (
                QuestionarioAvaliacao.objects.filter(
                    ativo=True, perguntas__isnull=False
                )
                .distinct()
                .order_by("-data_criacao")
            )
        except Exception:
            # Em migrações iniciais ou cenários sem tabelas, ignore
            pass
        if self.instance and self.instance.pk:
            try:
                # Tentar acessar o período letivo apenas se a instância já foi salva
                periodo_letivo = self.instance.periodo_letivo
                self.fields["turmas"].queryset = Turma.objects.filter(
                    periodo_letivo=periodo_letivo, status="ativa"
                )
            except:
                # Se não conseguir acessar o período letivo, mostra todas as turmas ativas
                self.fields["turmas"].queryset = Turma.objects.filter(status="ativa")
        else:
            # Para novas instâncias, mostrar todas as turmas ativas
            self.fields["turmas"].queryset = Turma.objects.filter(status="ativa")

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_fim = cleaned_data.get("data_fim")
        questionario = cleaned_data.get("questionario")

        if data_inicio and data_fim:
            if data_inicio >= data_fim:
                raise forms.ValidationError(
                    "A data de início deve ser anterior à data de fim."
                )

        # Impedir seleção de questionário sem perguntas
        if questionario:
            try:
                has_perguntas = QuestionarioPergunta.objects.filter(
                    questionario=questionario
                ).exists()
            except Exception:
                has_perguntas = (
                    True  # Evitar falsos positivos em migrações/checks iniciais
                )

            if not has_perguntas:
                self.add_error(
                    "questionario",
                    "O questionário selecionado não possui perguntas cadastradas. Cadastre perguntas antes de usá-lo em um ciclo.",
                )

        return cleaned_data


class QuestionarioAvaliacaoForm(forms.ModelForm):
    """
    Formulário para criar/editar questionários
    """

    class Meta:
        model = QuestionarioAvaliacao
        fields = ["titulo", "descricao", "ativo"]
        widgets = {
            "titulo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Título do questionário"}
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição opcional",
                }
            ),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CategoriaPerguntaForm(forms.ModelForm):
    """
    Formulário para criar/editar categorias de perguntas
    """

    class Meta:
        model = CategoriaPergunta
        fields = ["nome", "descricao", "ordem", "ativa"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Didática, Relacionamento",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Descrição da categoria",
                }
            ),
            "ordem": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ativa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PerguntaAvaliacaoForm(forms.ModelForm):
    """
    Formulário para criar/editar perguntas de avaliação
    """

    class Meta:
        model = PerguntaAvaliacao
        fields = [
            "enunciado",
            "tipo",
            "categoria",
            "ordem",
            "obrigatoria",
            "ativa",
            "opcoes_multipla_escolha",
        ]
        widgets = {
            "enunciado": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Digite a pergunta...",
                }
            ),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "categoria": forms.Select(attrs={"class": "form-control"}),
            "ordem": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "obrigatoria": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ativa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "opcoes_multipla_escolha": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": 'Para múltipla escolha, insira uma opção por linha. Também aceitamos CSV (separado por vírgula) ou JSON (ex.: ["A", "B"]).',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir valores padrão para campos obrigatórios
        if not self.instance.pk:
            self.fields["ordem"].initial = 0
            self.fields["obrigatoria"].initial = True
            self.fields["ativa"].initial = True

        # Exibir as opções de múltipla escolha (se existentes) como linhas no textarea
        try:
            opcoes = self.instance.opcoes_multipla_escolha
            if opcoes and isinstance(opcoes, (list, tuple)):
                self.fields["opcoes_multipla_escolha"].initial = "\n".join(
                    [str(o) for o in opcoes]
                )
        except Exception:
            pass

    def clean_opcoes_multipla_escolha(self):
        opcoes = self.cleaned_data.get("opcoes_multipla_escolha")
        tipo = self.cleaned_data.get("tipo")

        if tipo == "multipla_escolha":
            if not opcoes:
                raise forms.ValidationError(
                    "Opções são obrigatórias para perguntas de múltipla escolha."
                )

            # Normaliza opções vindas como string (linhas, CSV ou JSON)
            normalized = []
            if isinstance(opcoes, str):
                text = opcoes.strip()
                parsed = None
                # Tenta JSON primeiro se parecer um array
                if text.startswith("[") and text.endswith("]"):
                    try:
                        parsed = json.loads(text)
                    except Exception:
                        parsed = None
                if parsed is None:
                    # Considera quebras de linha como principal separador
                    parts = []
                    for line in text.split("\n"):
                        line = line.strip()
                        if not line:
                            continue
                        # Também quebra por vírgulas se houver
                        if "," in line:
                            parts.extend([p.strip() for p in line.split(",")])
                        else:
                            parts.append(line)
                    parsed = parts

                # Deduplica preservando ordem e remove vazios
                seen = set()
                for item in parsed:
                    s = str(item).strip()
                    if not s or s in seen:
                        continue
                    seen.add(s)
                    normalized.append(s)
            elif isinstance(opcoes, (list, tuple)):
                seen = set()
                for item in opcoes:
                    s = str(item).strip()
                    if not s or s in seen:
                        continue
                    seen.add(s)
                    normalized.append(s)
            else:
                raise forms.ValidationError("Formato inválido para as opções.")

            if len(normalized) < 2:
                raise forms.ValidationError(
                    "É necessário pelo menos 2 opções para múltipla escolha."
                )
            return normalized

        return opcoes


class RespostaAvaliacaoForm(forms.Form):
    """
    Formulário dinâmico para responder avaliações
    """

    def __init__(self, avaliacao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.avaliacao = avaliacao

        # Busca as perguntas do questionário do ciclo
        perguntas = avaliacao.ciclo.questionario.perguntas.select_related(
            "pergunta", "pergunta__categoria"
        ).order_by("ordem_no_questionario")

        for questionario_pergunta in perguntas:
            pergunta = questionario_pergunta.pergunta
            field_name = f"pergunta_{pergunta.id}"

            if pergunta.tipo == "likert":
                self.fields[field_name] = forms.ChoiceField(
                    label=pergunta.enunciado,
                    choices=[
                        (1, "1 - Discordo totalmente"),
                        (2, "2 - Discordo parcialmente"),
                        (3, "3 - Neutro"),
                        (4, "4 - Concordo parcialmente"),
                        (5, "5 - Concordo totalmente"),
                    ],
                    widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                    required=pergunta.obrigatoria,
                )

            elif pergunta.tipo == "nps":
                self.fields[field_name] = forms.ChoiceField(
                    label=pergunta.enunciado,
                    choices=[(i, str(i)) for i in range(11)],
                    widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                    required=pergunta.obrigatoria,
                )

            elif pergunta.tipo == "sim_nao":
                self.fields[field_name] = forms.ChoiceField(
                    label=pergunta.enunciado,
                    choices=[("true", "Sim"), ("false", "Não")],
                    widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                    required=pergunta.obrigatoria,
                )

            elif pergunta.tipo == "multipla_escolha":
                if pergunta.opcoes_multipla_escolha:
                    choices = [
                        (opcao, opcao) for opcao in pergunta.opcoes_multipla_escolha
                    ]
                    self.fields[field_name] = forms.ChoiceField(
                        label=pergunta.enunciado,
                        choices=choices,
                        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                        required=pergunta.obrigatoria,
                    )

            else:  # texto_livre
                self.fields[field_name] = forms.CharField(
                    label=pergunta.enunciado,
                    widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
                    required=pergunta.obrigatoria,
                )

    def save(self, aluno=None, session_key=None, anonima=False):
        """
        Salva as respostas da avaliação
        """
        respostas_salvas = []

        for field_name, valor in self.cleaned_data.items():
            if field_name.startswith("pergunta_"):
                pergunta_id = int(field_name.split("_")[1])
                pergunta = PerguntaAvaliacao.objects.get(id=pergunta_id)

                # Cria a resposta
                resposta = RespostaAvaliacao(
                    avaliacao=self.avaliacao,
                    pergunta=pergunta,
                    anonima=anonima,
                    session_key=session_key or "",
                )

                # Define o aluno se não for anônima
                if not anonima and aluno:
                    resposta.aluno = aluno

                # Define o valor baseado no tipo da pergunta
                if pergunta.tipo in ["likert", "nps", "multipla_escolha"]:
                    if pergunta.tipo == "multipla_escolha":
                        resposta.valor_texto = valor
                    else:
                        resposta.valor_numerico = int(valor)
                elif pergunta.tipo == "sim_nao":
                    resposta.valor_boolean = valor == "true"
                else:  # texto_livre
                    resposta.valor_texto = valor

                resposta.save()
                respostas_salvas.append(resposta)

        return respostas_salvas


class ComentarioAvaliacaoForm(forms.ModelForm):
    """
    Formulário para comentários adicionais na avaliação
    """

    class Meta:
        model = ComentarioAvaliacao
        fields = ["elogios", "sugestoes", "criticas_construtivas"]
        widgets = {
            "elogios": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Deixe seus elogios e pontos positivos...",
                }
            ),
            "sugestoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Deixe suas sugestões de melhoria...",
                }
            ),
            "criticas_construtivas": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Deixe críticas construtivas...",
                }
            ),
        }

    def save(self, avaliacao, aluno=None, session_key=None, anonimo=False, commit=True):
        comentario = super().save(commit=False)
        comentario.avaliacao = avaliacao
        comentario.anonimo = anonimo
        comentario.session_key = session_key or ""

        if not anonimo and aluno:
            comentario.aluno = aluno

        if commit:
            comentario.save()

        return comentario


class CategoriaPerguntaForm(forms.ModelForm):
    """
    Formulário para criar e editar categorias de perguntas
    """

    class Meta:
        model = CategoriaPergunta
        fields = ["nome", "descricao", "ordem", "ativa"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Didática, Relacionamento, Infraestrutura",
                    "maxlength": "50",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descrição opcional da categoria",
                    "rows": "3",
                }
            ),
            "ordem": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "999",
                    "placeholder": "0",
                }
            ),
            "ativa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "nome": "Nome da Categoria",
            "descricao": "Descrição",
            "ordem": "Ordem de Exibição",
            "ativa": "Categoria Ativa",
        }
        help_texts = {
            "nome": "Nome único para identificar a categoria",
            "descricao": "Descrição opcional para explicar o propósito da categoria",
            "ordem": "Ordem de exibição nas avaliações (menor número = primeiro)",
            "ativa": "Marque para manter a categoria ativa no sistema",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir ordem padrão se não especificada
        if not self.instance.pk:
            # Nova categoria - definir ordem como próxima disponível
            max_ordem = (
                CategoriaPergunta.objects.aggregate(max_ordem=models.Max("ordem"))[
                    "max_ordem"
                ]
                or 0
            )
            self.fields["ordem"].initial = max_ordem + 1

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")
        if nome:
            nome = nome.strip().title()

            # Verificar se já existe uma categoria com este nome
            qs = CategoriaPergunta.objects.filter(nome__iexact=nome)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    "Já existe uma categoria com este nome. Escolha um nome diferente."
                )

        return nome

    def clean_ordem(self):
        ordem = self.cleaned_data.get("ordem")
        if ordem is not None and ordem < 0:
            raise forms.ValidationError("A ordem não pode ser negativa.")
        return ordem
