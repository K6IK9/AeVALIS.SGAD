#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de teste realistas.

Popula todas as tabelas do sistema com dados variados:
- Usuários (alunos e professores)
- Cursos e períodos letivos
- Disciplinas e turmas
- Matrículas e horários
- Questionários e perguntas
- Ciclos de avaliação
- Avaliações e respostas

Uso:
    python scripts/popular_banco_dados.py
    python scripts/popular_banco_dados.py --clear  # Limpa antes de popular
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from avaliacao_docente.models import (
    PerfilAluno,
    PerfilProfessor,
    Curso,
    PeriodoLetivo,
    Disciplina,
    Turma,
    MatriculaTurma,
    HorarioTurma,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    CicloAvaliacao,
    AvaliacaoDocente,
    RespostaAvaliacao,
    ConfiguracaoSite,
)


class PopuladorBancoDados:
    """Classe para popular banco de dados com dados de teste"""

    def __init__(self, limpar_antes=False):
        self.limpar_antes = limpar_antes
        self.usuarios = []
        self.alunos = []
        self.professores = []
        self.cursos = []
        self.periodos = []
        self.disciplinas = []
        self.turmas = []
        self.matriculas = []
        self.questionarios = []
        self.categorias = []
        self.perguntas = []
        self.ciclos = []
        self.avaliacoes = []

    def run(self):
        """Executa população completa"""
        print("=" * 80)
        print("🚀 POPULAÇÃO DO BANCO DE DADOS")
        print("=" * 80)

        if self.limpar_antes:
            self.limpar_dados()

        print("\n📊 Criando dados...")
        self.criar_usuarios()
        self.criar_cursos()
        self.criar_periodos_letivos()
        self.criar_disciplinas()
        self.criar_turmas()
        self.criar_matriculas()
        self.criar_horarios()
        self.criar_questionarios()
        self.criar_ciclos_avaliacao()
        self.criar_avaliacoes()
        self.criar_respostas()
        self.criar_configuracao_site()

        self.exibir_resumo()

        print("\n✅ POPULAÇÃO CONCLUÍDA!")

    def limpar_dados(self):
        """Limpa todos os dados de teste"""
        print("\n🧹 Limpando dados existentes...")

        # Ordem reversa de dependências
        RespostaAvaliacao.objects.all().delete()
        AvaliacaoDocente.objects.all().delete()
        CicloAvaliacao.objects.all().delete()
        QuestionarioPergunta.objects.all().delete()
        PerguntaAvaliacao.objects.all().delete()
        CategoriaPergunta.objects.all().delete()
        QuestionarioAvaliacao.objects.all().delete()
        HorarioTurma.objects.all().delete()
        MatriculaTurma.objects.all().delete()
        Turma.objects.all().delete()
        Disciplina.objects.all().delete()
        PeriodoLetivo.objects.all().delete()
        Curso.objects.all().delete()
        PerfilAluno.objects.all().delete()
        PerfilProfessor.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        print("   ✅ Dados limpos")

    def criar_usuarios(self):
        """Cria usuários (alunos e professores)"""
        print("\n👥 Criando usuários...")

        # Verificar se já existem usuários
        if User.objects.filter(username__startswith="prof.").exists():
            print("   ℹ️  Usuários já existem, usando existentes...")
            self.professores = list(PerfilProfessor.objects.all())
            self.alunos = list(PerfilAluno.objects.all())
            self.usuarios = list(User.objects.filter(is_superuser=False))
            print(f"   ✅ {len(self.professores)} professores encontrados")
            print(f"   ✅ {len(self.alunos)} alunos encontrados")
            return

        # Professores
        nomes_professores = [
            ("João", "Silva", "Matemática"),
            ("Maria", "Santos", "Física"),
            ("Pedro", "Oliveira", "Química"),
            ("Ana", "Costa", "Biologia"),
            ("Carlos", "Souza", "História"),
            ("Julia", "Lima", "Geografia"),
            ("Roberto", "Alves", "Português"),
            ("Fernanda", "Rodrigues", "Inglês"),
            ("Paulo", "Martins", "Programação"),
            ("Mariana", "Ferreira", "Algoritmos"),
            ("Lucas", "Pereira", "Estrutura de Dados"),
            ("Beatriz", "Gomes", "Banco de Dados"),
            ("Ricardo", "Barbosa", "Redes"),
            ("Camila", "Ribeiro", "Sistemas Operacionais"),
            ("André", "Carvalho", "Engenharia de Software"),
        ]

        for idx, (nome, sobrenome, especialidade) in enumerate(nomes_professores, 1):
            username = f"prof.{nome.lower()}.{sobrenome.lower()}"
            user = User.objects.create_user(
                username=username,
                email=f"{username}@escola.edu.br",
                password="senha123",
                first_name=nome,
                last_name=sobrenome,
            )

            professor = PerfilProfessor.objects.create(
                user=user,
                registro_academico=f"PROF{idx:04d}",
            )

            self.usuarios.append(user)
            self.professores.append(professor)

        print(f"   ✅ {len(self.professores)} professores criados")

        # Alunos
        nomes_alunos = [
            ("Gabriel", "Oliveira"),
            ("Larissa", "Silva"),
            ("Rafael", "Santos"),
            ("Amanda", "Costa"),
            ("Bruno", "Almeida"),
            ("Carolina", "Lima"),
            ("Diego", "Ferreira"),
            ("Eduarda", "Rodrigues"),
            ("Felipe", "Martins"),
            ("Giovana", "Pereira"),
            ("Henrique", "Gomes"),
            ("Isabela", "Barbosa"),
            ("João Pedro", "Ribeiro"),
            ("Letícia", "Carvalho"),
            ("Matheus", "Araújo"),
            ("Natália", "Dias"),
            ("Otávio", "Cardoso"),
            ("Patrícia", "Nunes"),
            ("Rodrigo", "Teixeira"),
            ("Sophia", "Mendes"),
            ("Thiago", "Sousa"),
            ("Valentina", "Castro"),
            ("Wesley", "Azevedo"),
            ("Yasmin", "Pinto"),
            ("Arthur", "Moreira"),
            ("Bianca", "Correia"),
            ("Caio", "Monteiro"),
            ("Daniela", "Nascimento"),
            ("Enzo", "Campos"),
            ("Fernanda", "Vieira"),
            ("Guilherme", "Freitas"),
            ("Helena", "Rocha"),
            ("Igor", "Duarte"),
            ("Júlia", "Fernandes"),
            ("Kevin", "Ramos"),
            ("Lara", "Cunha"),
            ("Miguel", "Santana"),
            ("Nicole", "Melo"),
            ("Paulo", "Pires"),
            ("Rafaela", "Farias"),
            ("Samuel", "Cavalcanti"),
            ("Tatiane", "Macedo"),
            ("Vítor", "Gonçalves"),
            ("Wanessa", "Bezerra"),
            ("Xavier", "Miranda"),
            ("Yara", "Tavares"),
            ("Zélia", "Reis"),
            ("Alexandre", "Borges"),
            ("Bruna", "Lopes"),
            ("Cristiano", "Medeiros"),
        ]

        for idx, (nome, sobrenome) in enumerate(nomes_alunos, 1):
            username = f"aluno.{nome.lower().replace(' ', '')}.{sobrenome.lower()}"
            # Criar username único que servirá como matrícula
            matricula = f"ALU{2024000 + idx}"
            user = User.objects.create_user(
                username=matricula,  # Usar matrícula como username
                email=f"{username[:30]}@aluno.escola.edu.br",
                password="senha123",
                first_name=nome,
                last_name=sobrenome,
            )

            aluno = PerfilAluno.objects.create(user=user, situacao="Ativo")

            self.usuarios.append(user)
            self.alunos.append(aluno)

        print(f"   ✅ {len(self.alunos)} alunos criados")

    def criar_cursos(self):
        """Cria cursos"""
        print("\n📚 Criando cursos...")

        # Verificar se já existem cursos
        if Curso.objects.exists():
            print("   ℹ️  Cursos já existem, usando existentes...")
            self.cursos = list(Curso.objects.all())
            print(f"   ✅ {len(self.cursos)} cursos encontrados")
            return

        cursos_data = [
            ("Ciência da Computação", "CC"),
            ("Sistemas de Informação", "SI"),
            ("Engenharia de Software", "ES"),
            ("Análise e Desenvolvimento de Sistemas", "ADS"),
            ("Redes de Computadores", "RC"),
            ("Segurança da Informação", "SEG"),
        ]

        for nome, sigla in cursos_data:
            coordenador = random.choice(self.professores)
            curso = Curso.objects.create(
                curso_nome=nome, curso_sigla=sigla, coordenador_curso=coordenador
            )
            self.cursos.append(curso)

        print(f"   ✅ {len(self.cursos)} cursos criados")

    def criar_periodos_letivos(self):
        """Cria períodos letivos"""
        print("\n📅 Criando períodos letivos...")

        # Verificar se já existem períodos
        if PeriodoLetivo.objects.exists():
            print("   ℹ️  Períodos já existem, usando existentes...")
            self.periodos = list(PeriodoLetivo.objects.all())
            print(f"   ✅ {len(self.periodos)} períodos encontrados")
            return

        anos = [2023, 2024, 2025]
        semestres = [1, 2]

        for ano in anos:
            for semestre in semestres:
                periodo = PeriodoLetivo.objects.create(
                    nome=f"{ano}.{semestre}", ano=ano, semestre=semestre
                )
                self.periodos.append(periodo)

        print(f"   ✅ {len(self.periodos)} períodos letivos criados")

    def criar_disciplinas(self):
        """Cria disciplinas"""
        print("\n📖 Criando disciplinas...")

        # Verificar se já existem disciplinas
        if Disciplina.objects.count() > 10:
            print("   ℹ️  Disciplinas já existem, usando existentes...")
            self.disciplinas = list(Disciplina.objects.all())
            print(f"   ✅ {len(self.disciplinas)} disciplinas encontradas")
            return

        disciplinas_por_curso = {
            "CC": [
                "Algoritmos e Programação",
                "Estrutura de Dados",
                "Banco de Dados I",
                "Banco de Dados II",
                "Programação Orientada a Objetos",
                "Desenvolvimento Web",
                "Engenharia de Software",
                "Sistemas Operacionais",
                "Redes de Computadores",
                "Inteligência Artificial",
            ],
            "SI": [
                "Fundamentos de Sistemas de Informação",
                "Análise de Sistemas",
                "Gestão de Projetos",
                "Governança de TI",
                "Business Intelligence",
            ],
            "ES": [
                "Requisitos de Software",
                "Arquitetura de Software",
                "Testes de Software",
                "DevOps",
                "Qualidade de Software",
            ],
            "ADS": [
                "Lógica de Programação",
                "Desenvolvimento Mobile",
                "Frameworks Web",
                "APIs RESTful",
            ],
            "RC": [
                "Fundamentos de Redes",
                "Protocolo TCP/IP",
                "Segurança em Redes",
                "Administração de Redes",
            ],
            "SEG": [
                "Criptografia",
                "Segurança de Aplicações",
                "Ethical Hacking",
                "Forense Digital",
            ],
        }

        tipos = ["Obrigatória", "Optativa"]

        for curso in self.cursos:
            disciplinas_curso = disciplinas_por_curso.get(curso.curso_sigla, [])

            for idx, nome_disc in enumerate(disciplinas_curso, 1):
                # Usar períodos mais recentes (2024.1, 2024.2, 2025.1)
                periodo = random.choice(self.periodos[-3:])
                professor = random.choice(self.professores)

                disciplina = Disciplina.objects.create(
                    disciplina_nome=nome_disc,
                    disciplina_sigla=f"{curso.curso_sigla}{idx:02d}",
                    disciplina_tipo=random.choice(tipos),
                    curso=curso,
                    professor=professor,
                    periodo_letivo=periodo,
                )
                self.disciplinas.append(disciplina)

        print(f"   ✅ {len(self.disciplinas)} disciplinas criadas")

    def criar_turmas(self):
        """Cria turmas"""
        print("\n🏫 Criando turmas...")

        # Verificar se já existem turmas
        if Turma.objects.count() > 10:
            print("   ℹ️  Turmas já existem, usando existentes...")
            self.turmas = list(Turma.objects.all())
            print(f"   ✅ {len(self.turmas)} turmas encontradas")
            return

        turnos = ["matutino", "vespertino", "noturno"]

        for disciplina in self.disciplinas:
            # Algumas disciplinas têm múltiplas turmas
            num_turmas = random.choices([1, 2, 3], weights=[60, 30, 10])[0]

            turnos_usados = random.sample(turnos, num_turmas)

            for turno in turnos_usados:
                turma = Turma.objects.create(
                    disciplina=disciplina,
                    turno=turno,
                    data_criacao=timezone.now()
                    - timedelta(days=random.randint(30, 180)),
                )
                self.turmas.append(turma)

        print(f"   ✅ {len(self.turmas)} turmas criadas")

    def criar_matriculas(self):
        """Cria matrículas de alunos em turmas"""
        print("\n📝 Criando matrículas...")

        # Verificar se já existem matrículas
        if MatriculaTurma.objects.count() > 20:
            print("   ℹ️  Matrículas já existem, usando existentes...")
            self.matriculas = list(MatriculaTurma.objects.all())
            print(f"   ✅ {len(self.matriculas)} matrículas encontradas")
            return

        status_opcoes = ["ativo", "trancado", "concluido"]

        for aluno in self.alunos:
            # Cada aluno se matricula em 3-7 turmas
            num_matriculas = random.randint(3, 7)
            turmas_aluno = random.sample(
                self.turmas, min(num_matriculas, len(self.turmas))
            )

            for turma in turmas_aluno:
                status = random.choices(
                    status_opcoes, weights=[80, 10, 10]  # 80% ativo
                )[0]

                matricula = MatriculaTurma.objects.create(
                    aluno=aluno,
                    turma=turma,
                    status=status,
                    data_matricula=turma.data_criacao
                    + timedelta(days=random.randint(1, 15)),
                )
                self.matriculas.append(matricula)

        print(f"   ✅ {len(self.matriculas)} matrículas criadas")

    def criar_horarios(self):
        """Cria horários das turmas"""
        print("\n🕐 Criando horários...")

        dias_semana = [
            ("segunda-feira", 1),
            ("terça-feira", 2),
            ("quarta-feira", 3),
            ("quinta-feira", 4),
            ("sexta-feira", 5),
        ]

        horarios_turno = {
            "matutino": [("07:00", "08:40"), ("08:50", "10:30"), ("10:40", "12:20")],
            "vespertino": [("13:00", "14:40"), ("14:50", "16:30"), ("16:40", "18:20")],
            "noturno": [("18:30", "20:10"), ("20:20", "22:00")],
        }

        for turma in self.turmas:
            # 2 aulas por semana
            dias_aula = random.sample(dias_semana, 2)
            horarios_disponiveis = horarios_turno[turma.turno]
            horario = random.choice(horarios_disponiveis)

            for dia_nome, dia_num in dias_aula:
                HorarioTurma.objects.create(
                    turma=turma,
                    dia_semana=dia_num,
                    hora_inicio=horario[0],
                    hora_fim=horario[1],
                )

        horarios_count = HorarioTurma.objects.count()
        print(f"   ✅ {horarios_count} horários criados")

    def criar_questionarios(self):
        """Cria questionários e perguntas"""
        print("\n📋 Criando questionários e perguntas...")

        # Verificar se já existem questionários
        if QuestionarioAvaliacao.objects.exists():
            print("   ℹ️  Questionários já existem, usando existentes...")
            self.questionarios = list(QuestionarioAvaliacao.objects.all())
            self.categorias = list(CategoriaPergunta.objects.all())
            self.perguntas = list(PerguntaAvaliacao.objects.all())
            print(f"   ✅ {len(self.questionarios)} questionários encontrados")
            print(f"   ✅ {len(self.categorias)} categorias encontradas")
            print(f"   ✅ {len(self.perguntas)} perguntas encontradas")
            return

        # Criar categorias
        categorias_data = [
            ("Didática", "Avalia métodos de ensino do professor"),
            ("Conhecimento", "Avalia domínio do conteúdo"),
            ("Relacionamento", "Avalia relacionamento com alunos"),
            ("Recursos", "Avalia uso de recursos didáticos"),
            ("Avaliação", "Avalia métodos avaliativos"),
            ("Pontualidade", "Avalia cumprimento de horários"),
        ]

        for nome, desc in categorias_data:
            categoria = CategoriaPergunta.objects.create(nome=nome, descricao=desc)
            self.categorias.append(categoria)

        # Criar questionário
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username="admin", email="admin@escola.edu.br", password="admin123"
            )

        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Avaliação Docente 2024",
            descricao="Questionário padrão para avaliação de professores",
            ativo=True,
            criado_por=admin_user,
        )
        self.questionarios.append(questionario)

        # Criar perguntas por categoria
        perguntas_por_categoria = {
            "Didática": [
                "O professor explica o conteúdo de forma clara e objetiva?",
                "As aulas são dinâmicas e motivadoras?",
                "O professor utiliza exemplos práticos?",
                "O ritmo das aulas é adequado?",
            ],
            "Conhecimento": [
                "O professor demonstra domínio do conteúdo?",
                "O professor consegue responder dúvidas com clareza?",
                "O professor relaciona teoria e prática?",
            ],
            "Relacionamento": [
                "O professor é acessível e receptivo?",
                "O professor trata os alunos com respeito?",
                "O professor estimula a participação?",
            ],
            "Recursos": [
                "Os materiais didáticos são adequados?",
                "O professor utiliza recursos tecnológicos?",
                "As referências bibliográficas são suficientes?",
            ],
            "Avaliação": [
                "As avaliações são coerentes com o conteúdo?",
                "Os critérios de avaliação são claros?",
                "O feedback sobre avaliações é adequado?",
            ],
            "Pontualidade": [
                "O professor cumpre os horários de aula?",
                "O professor respeita o tempo de intervalo?",
            ],
        }

        ordem = 1
        for categoria in self.categorias:
            perguntas_cat = perguntas_por_categoria.get(categoria.nome, [])

            for texto in perguntas_cat:
                pergunta = PerguntaAvaliacao.objects.create(
                    categoria=categoria,
                    enunciado=texto,
                    tipo="likert",
                    obrigatoria=True,
                )
                self.perguntas.append(pergunta)

                # Associar ao questionário
                QuestionarioPergunta.objects.create(
                    questionario=questionario,
                    pergunta=pergunta,
                    ordem_no_questionario=ordem,
                )
                ordem += 1

        # Adicionar pergunta aberta
        pergunta_aberta = PerguntaAvaliacao.objects.create(
            categoria=self.categorias[0],
            enunciado="Comentários ou sugestões adicionais:",
            tipo="texto_livre",
            obrigatoria=False,
        )
        self.perguntas.append(pergunta_aberta)

        QuestionarioPergunta.objects.create(
            questionario=questionario,
            pergunta=pergunta_aberta,
            ordem_no_questionario=ordem,
        )

        print(f"   ✅ {len(self.categorias)} categorias criadas")
        print(f"   ✅ {len(self.questionarios)} questionário criado")
        print(f"   ✅ {len(self.perguntas)} perguntas criadas")

    def criar_ciclos_avaliacao(self):
        """Cria ciclos de avaliação"""
        print("\n🔄 Criando ciclos de avaliação...")

        # Verificar se já existem ciclos
        if CicloAvaliacao.objects.exists():
            print("   ℹ️  Ciclos já existem, usando existentes...")
            self.ciclos = list(CicloAvaliacao.objects.all())
            print(f"   ✅ {len(self.ciclos)} ciclos encontrados")
            return

        questionario = self.questionarios[0]

        # Ciclo 2024.1 (encerrado)
        periodo_2024_1 = PeriodoLetivo.objects.get(nome="2024.1")
        ciclo_2024_1 = CicloAvaliacao.objects.create(
            nome="Ciclo 2024.1",
            periodo_letivo=periodo_2024_1,
            questionario=questionario,
            data_inicio=(timezone.now() - timedelta(days=120)),
            data_fim=(timezone.now() - timedelta(days=60)),
            enviar_lembrete_email=True,
            criado_por=self.professores[0].user,
        )

        # Adicionar turmas do período 2024.1
        turmas_2024_1 = [
            t for t in self.turmas if t.disciplina.periodo_letivo.nome == "2024.1"
        ]
        ciclo_2024_1.turmas.set(turmas_2024_1[:20])  # Limitar para performance

        self.ciclos.append(ciclo_2024_1)

        # Ciclo 2024.2 (em andamento)
        periodo_2024_2 = PeriodoLetivo.objects.get(nome="2024.2")
        ciclo_2024_2 = CicloAvaliacao.objects.create(
            nome="Ciclo 2024.2",
            periodo_letivo=periodo_2024_2,
            questionario=questionario,
            data_inicio=(timezone.now() - timedelta(days=30)),
            data_fim=(timezone.now() + timedelta(days=30)),
            enviar_lembrete_email=True,
            criado_por=self.professores[0].user,
        )

        turmas_2024_2 = [
            t for t in self.turmas if t.disciplina.periodo_letivo.nome == "2024.2"
        ]
        ciclo_2024_2.turmas.set(turmas_2024_2[:20])

        self.ciclos.append(ciclo_2024_2)

        # Ciclo 2025.1 (futuro)
        periodo_2025_1 = PeriodoLetivo.objects.get(nome="2025.1")
        ciclo_2025_1 = CicloAvaliacao.objects.create(
            nome="Ciclo 2025.1",
            periodo_letivo=periodo_2025_1,
            questionario=questionario,
            data_inicio=(timezone.now() + timedelta(days=60)),
            data_fim=(timezone.now() + timedelta(days=150)),
            enviar_lembrete_email=True,
            criado_por=self.professores[0].user,
        )

        turmas_2025_1 = [
            t for t in self.turmas if t.disciplina.periodo_letivo.nome == "2025.1"
        ]
        ciclo_2025_1.turmas.set(turmas_2025_1[:20])

        self.ciclos.append(ciclo_2025_1)

        print(f"   ✅ {len(self.ciclos)} ciclos de avaliação criados")

    def criar_avaliacoes(self):
        """Cria avaliações (via signal automático ao adicionar turmas ao ciclo)"""
        print("\n⭐ Criando avaliações...")

        # As avaliações são criadas automaticamente por signals
        # Vamos apenas contar
        avaliacoes = AvaliacaoDocente.objects.all()
        self.avaliacoes = list(avaliacoes)

        print(f"   ✅ {len(self.avaliacoes)} avaliações criadas (via signals)")

    def criar_respostas(self):
        """Cria respostas de alunos"""
        print("\n💬 Criando respostas...")

        # Pegar avaliações do ciclo 2024.1 (encerrado) para ter respostas
        avaliacoes_ciclo_1 = [a for a in self.avaliacoes if a.ciclo == self.ciclos[0]]

        respostas_likert = [1, 2, 3, 4, 5]
        comentarios_positivos = [
            "Excelente professor, muito didático!",
            "Aulas muito boas, aprendi bastante.",
            "Professor competente e atencioso.",
            "Ótima didática e domínio do conteúdo.",
            "Aulas dinâmicas e interessantes.",
        ]
        comentarios_negativos = [
            "Poderia ser mais dinâmico.",
            "Alguns tópicos ficaram confusos.",
            "Ritmo das aulas um pouco rápido.",
        ]

        respostas_count = 0

        for avaliacao in avaliacoes_ciclo_1[:30]:  # Limitar para performance
            # 50-80% dos alunos respondem
            matriculas_turma = MatriculaTurma.objects.filter(
                turma=avaliacao.turma, status="ativo"
            )

            num_respondentes = int(matriculas_turma.count() * random.uniform(0.5, 0.8))
            respondentes = random.sample(
                list(matriculas_turma), min(num_respondentes, matriculas_turma.count())
            )

            for matricula in respondentes:
                # Marcar avaliação como em andamento
                if avaliacao.status == "pendente":
                    avaliacao.status = "em_andamento"
                    avaliacao.save()

                # Responder perguntas Likert
                perguntas_likert = [
                    p for p in self.perguntas if p.tipo_pergunta == "escala_likert"
                ]

                # Tendência: 70% respostas positivas (4-5), 20% neutras (3), 10% negativas (1-2)
                for pergunta in perguntas_likert:
                    nota = random.choices(
                        respostas_likert,
                        weights=[5, 5, 20, 35, 35],  # Distribuição realista
                    )[0]

                    RespostaAvaliacao.objects.create(
                        avaliacao=avaliacao, pergunta=pergunta, resposta_likert=nota
                    )
                    respostas_count += 1

                # Responder pergunta aberta (50% respondem)
                if random.random() < 0.5:
                    pergunta_aberta = [
                        p for p in self.perguntas if p.tipo_pergunta == "texto_longo"
                    ][0]

                    # Comentário baseado na média das notas
                    media_notas = (
                        sum(
                            [
                                r.resposta_likert
                                for r in RespostaAvaliacao.objects.filter(
                                    avaliacao=avaliacao
                                )
                            ]
                        )
                        / RespostaAvaliacao.objects.filter(avaliacao=avaliacao).count()
                    )

                    if media_notas >= 4:
                        comentario = random.choice(comentarios_positivos)
                    elif media_notas >= 3:
                        comentario = "Bom professor, algumas melhorias são possíveis."
                    else:
                        comentario = random.choice(comentarios_negativos)

                    RespostaAvaliacao.objects.create(
                        avaliacao=avaliacao,
                        pergunta=pergunta_aberta,
                        resposta_texto=comentario,
                    )
                    respostas_count += 1

                # Marcar avaliação como concluída
                avaliacao.status = "concluida"
                avaliacao.data_conclusao = timezone.now() - timedelta(
                    days=random.randint(1, 30)
                )
                avaliacao.save()

        print(f"   ✅ {respostas_count} respostas criadas")

    def criar_configuracao_site(self):
        """Cria configuração do site"""
        print("\n⚙️ Criando configuração do site...")

        if not ConfiguracaoSite.objects.exists():
            ConfiguracaoSite.objects.create(
                metodo_envio_email="smtp", email_notificacao_erros="admin@escola.edu.br"
            )
            print("   ✅ Configuração do site criada")
        else:
            print("   ℹ️  Configuração do site já existe")

    def exibir_resumo(self):
        """Exibe resumo dos dados criados"""
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("=" * 80)

        print(f"\n👥 Usuários:")
        print(f"   - Professores: {len(self.professores)}")
        print(f"   - Alunos: {len(self.alunos)}")
        print(f"   - Total: {len(self.usuarios)}")

        print(f"\n📚 Acadêmico:")
        print(f"   - Cursos: {len(self.cursos)}")
        print(f"   - Períodos letivos: {len(self.periodos)}")
        print(f"   - Disciplinas: {len(self.disciplinas)}")
        print(f"   - Turmas: {len(self.turmas)}")
        print(f"   - Matrículas: {len(self.matriculas)}")
        print(f"   - Horários: {HorarioTurma.objects.count()}")

        print(f"\n📋 Avaliações:")
        print(f"   - Questionários: {len(self.questionarios)}")
        print(f"   - Categorias: {len(self.categorias)}")
        print(f"   - Perguntas: {len(self.perguntas)}")
        print(f"   - Ciclos: {len(self.ciclos)}")
        print(f"   - Avaliações: {len(self.avaliacoes)}")
        print(f"   - Respostas: {RespostaAvaliacao.objects.count()}")

        print(f"\n⚙️ Configuração:")
        print(f"   - Configurações do site: {ConfiguracaoSite.objects.count()}")

        # Estatísticas adicionais
        print(f"\n📈 Estatísticas:")
        avaliacoes_concluidas = AvaliacaoDocente.objects.filter(
            status="concluida"
        ).count()
        avaliacoes_pendentes = AvaliacaoDocente.objects.filter(
            status="pendente"
        ).count()
        print(f"   - Avaliações concluídas: {avaliacoes_concluidas}")
        print(f"   - Avaliações pendentes: {avaliacoes_pendentes}")

        if avaliacoes_concluidas > 0:
            taxa_resposta = (avaliacoes_concluidas / len(self.avaliacoes)) * 100
            print(f"   - Taxa de resposta: {taxa_resposta:.1f}%")

        media_matriculas = len(self.matriculas) / len(self.alunos) if self.alunos else 0
        print(f"   - Média de matrículas por aluno: {media_matriculas:.1f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Popular banco de dados com dados de teste"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Limpar dados antes de popular"
    )
    args = parser.parse_args()

    populador = PopuladorBancoDados(limpar_antes=args.clear)
    populador.run()
