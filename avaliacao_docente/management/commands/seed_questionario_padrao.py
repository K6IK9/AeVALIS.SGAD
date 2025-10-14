"""
Comando de management para criar o questionário padrão de avaliação docente.
Execução idempotente: pode ser rodado múltiplas vezes sem duplicar dados.

Uso:
    python manage.py seed_questionario_padrao
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avaliacao_docente.models import (
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioAvaliacao,
    QuestionarioPergunta,
)


class Command(BaseCommand):
    help = "Cria o questionário padrão de avaliação docente com 10 perguntas"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "\n========== Seed: Questionário Padrão de Avaliação Docente =========="
            )
        )

        # 1. Criar ou obter categoria
        categoria, created = CategoriaPergunta.objects.get_or_create(
            nome="Atividades de Ensino / Atuação Pedagógica",
            defaults={
                "descricao": "Perguntas relacionadas à atuação pedagógica e didática do docente",
                "ordem": 1,
                "ativo": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Categoria criada: {categoria.nome}")
            )
        else:
            self.stdout.write(f"  Categoria já existe: {categoria.nome}")

        # 2. Criar ou obter questionário
        # Usar um usuário admin existente como criador (ou criar um genérico)
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user, _ = User.objects.get_or_create(
                username="system",
                defaults={
                    "email": "system@sistema.local",
                    "is_staff": True,
                    "is_superuser": True,
                },
            )

        questionario, created = QuestionarioAvaliacao.objects.get_or_create(
            titulo="Avaliação Docente — Padrão",
            defaults={
                "descricao": "Questionário padrão baseado na Resolução CONSUP/IFMT Nº 87-2023 para avaliação de desempenho docente",
                "criado_por": admin_user,
                "ativo": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Questionário criado: {questionario.titulo}")
            )
        else:
            self.stdout.write(f"  Questionário já existe: {questionario.titulo}")

        # 3. Definir as 10 perguntas padrão
        perguntas_data = [
            "Informa o programa/plano de ensino e deixa claro o objetivo da disciplina.",
            "Demonstra clareza e objetividade na explicação dos conteúdos da disciplina.",
            "Relaciona os conceitos teóricos com a prática do cotidiano.",
            "Indica fontes de consulta (sites, livros, artigos, etc.) relacionadas à disciplina.",
            "Utiliza recursos didáticos de forma que promova o aprendizado.",
            "Proporciona oportunidades de questionamentos e esclarecimentos de dúvidas relevantes.",
            "Apresenta previamente os critérios de avaliação aos alunos.",
            "Estabelece uma relação de respeito com os estudantes.",
            "Estimula os alunos a relacionar o conhecimento com outras disciplinas.",
            "Exige nas avaliações de aprendizagem os conteúdos desenvolvidos.",
        ]

        # Opções de resposta fixas para todas as perguntas
        opcoes_resposta = [
            "Não atende",
            "Insuficiente",
            "Regular",
            "Bom",
            "Excelente",
        ]

        # 4. Criar perguntas e associar ao questionário
        perguntas_criadas = 0
        perguntas_existentes = 0

        for ordem, enunciado in enumerate(perguntas_data, start=1):
            # Criar ou obter a pergunta
            pergunta, created = PerguntaAvaliacao.objects.get_or_create(
                enunciado=enunciado,
                categoria=categoria,
                defaults={
                    "tipo": "multipla_escolha",
                    "obrigatoria": True,
                    "opcoes_multipla_escolha": opcoes_resposta,
                    "ativo": True,
                },
            )

            if created:
                perguntas_criadas += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Pergunta {ordem} criada: {enunciado[:60]}..."
                    )
                )
            else:
                perguntas_existentes += 1
                # Atualizar opções se necessário
                if pergunta.opcoes_multipla_escolha != opcoes_resposta:
                    pergunta.opcoes_multipla_escolha = opcoes_resposta
                    pergunta.save()
                    self.stdout.write(
                        f"    Pergunta {ordem} atualizada: {enunciado[:60]}..."
                    )

            # Associar pergunta ao questionário (se ainda não estiver associada)
            qp, qp_created = QuestionarioPergunta.objects.get_or_create(
                questionario=questionario,
                pergunta=pergunta,
                defaults={"ordem_no_questionario": ordem, "ativo": True},
            )

            if not qp_created and qp.ordem_no_questionario != ordem:
                # Atualizar ordem se mudou
                qp.ordem_no_questionario = ordem
                qp.save()

        # 5. Sumário final
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("Seed concluído com sucesso!"))
        self.stdout.write(f"  Categoria: {categoria.nome}")
        self.stdout.write(f"  Questionário: {questionario.titulo}")
        self.stdout.write(f"  Perguntas criadas: {perguntas_criadas}")
        self.stdout.write(f"  Perguntas já existentes: {perguntas_existentes}")
        self.stdout.write(
            f"  Total de perguntas no questionário: {questionario.perguntas.count()}"
        )
        self.stdout.write("=" * 70 + "\n")
