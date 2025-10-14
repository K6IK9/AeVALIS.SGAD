"""
Comando para testar os cálculos de média do questionário padrão.
"""

from django.core.management.base import BaseCommand
from avaliacao_docente.models import AvaliacaoDocente, PerguntaAvaliacao


class Command(BaseCommand):
    help = "Testa os cálculos de média do questionário padrão"

    def add_arguments(self, parser):
        parser.add_argument(
            "--avaliacao-id",
            type=int,
            help="ID da avaliação para testar (opcional, usa a primeira se não especificado)",
        )

    def handle(self, *args, **options):
        avaliacao_id = options.get("avaliacao_id")

        if avaliacao_id:
            try:
                avaliacao = AvaliacaoDocente.objects.get(id=avaliacao_id)
            except AvaliacaoDocente.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Avaliação com ID {avaliacao_id} não encontrada.")
                )
                return
        else:
            # Pegar primeira avaliação com respostas
            avaliacao = (
                AvaliacaoDocente.objects.filter(respostas__isnull=False)
                .distinct()
                .first()
            )
            if not avaliacao:
                self.stdout.write(
                    self.style.ERROR("Nenhuma avaliação com respostas encontrada.")
                )
                return

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.SUCCESS(f"📊 TESTE DE CÁLCULOS - Avaliação ID: {avaliacao.id}")
        )
        self.stdout.write(f"Professor: {avaliacao.professor}")
        self.stdout.write(f"Disciplina: {avaliacao.disciplina}")
        self.stdout.write(f"Turma: {avaliacao.turma}")
        self.stdout.write("=" * 80 + "\n")

        # Testar cálculo por pergunta
        perguntas = (
            PerguntaAvaliacao.objects.filter(
                respostas__avaliacao=avaliacao, tipo="multipla_escolha"
            )
            .distinct()
            .order_by("id")
        )

        if not perguntas.exists():
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Nenhuma pergunta de múltipla escolha encontrada nesta avaliação."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("📝 MÉDIAS POR PERGUNTA:\n"))

        for i, pergunta in enumerate(perguntas, 1):
            resultado = avaliacao.calcular_media_pergunta(pergunta)

            if not resultado:
                self.stdout.write(f"{i}. {pergunta.enunciado[:60]}...")
                self.stdout.write(self.style.WARNING("   ⚠️  Sem respostas\n"))
                continue

            self.stdout.write(
                f"{i}. {pergunta.enunciado[:60]}{'...' if len(pergunta.enunciado) > 60 else ''}"
            )
            self.stdout.write(
                f"   Média: {self.style.SUCCESS(str(resultado['media']))}"
            )
            self.stdout.write(f"   Respondentes: {resultado['total_respondentes']}")
            self.stdout.write(f"   Contagens:")
            for opcao, count in resultado["contagens"].items():
                peso = avaliacao.OPCOES_PESOS[opcao]
                self.stdout.write(f"      • {opcao}: {count} (peso {peso})")
            self.stdout.write("")

        # Testar média geral
        self.stdout.write("\n" + "-" * 80)
        self.stdout.write(self.style.SUCCESS("📊 MÉDIA GERAL:\n"))

        resultado_geral = avaliacao.calcular_media_geral_questionario_padrao()

        if not resultado_geral:
            self.stdout.write(
                self.style.WARNING("⚠️  Não foi possível calcular média geral")
            )
            return

        self.stdout.write(
            f"Média Geral: {self.style.SUCCESS(str(resultado_geral['media_geral']))}"
        )
        self.stdout.write(f"Total de Perguntas: {resultado_geral['total_perguntas']}")

        classificacao = avaliacao.get_classificacao_media(
            resultado_geral["media_geral"]
        )
        cor_style = self.style.SUCCESS
        if classificacao in ["Não atende", "Insuficiente"]:
            cor_style = self.style.ERROR
        elif classificacao == "Regular":
            cor_style = self.style.WARNING

        self.stdout.write(f"Classificação: {cor_style(classificacao)}")

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.SUCCESS("✅ Teste de cálculos concluído com sucesso!")
        )
        self.stdout.write("=" * 80 + "\n")
