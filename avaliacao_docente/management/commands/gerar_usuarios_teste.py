from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avaliacao_docente.models import PerfilAluno, PerfilProfessor
from rolepermissions.roles import assign_role
import random


class Command(BaseCommand):
    help = "Gera 50 usuários de teste com diferentes roles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--quantidade",
            type=int,
            default=50,
            help="Quantidade de usuários para criar (padrão: 50)",
        )

    def handle(self, *args, **options):
        quantidade = options["quantidade"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Iniciando criação de {quantidade} usuários de teste..."
            )
        )

        # Nomes e sobrenomes para gerar dados realistas
        nomes = [
            "Ana",
            "João",
            "Maria",
            "Pedro",
            "Carla",
            "Lucas",
            "Fernanda",
            "Rafael",
            "Juliana",
            "Bruno",
            "Camila",
            "Thiago",
            "Larissa",
            "Diego",
            "Beatriz",
            "Gabriel",
            "Amanda",
            "Felipe",
            "Gabriela",
            "Mateus",
            "Letícia",
            "André",
            "Priscila",
            "Rodrigo",
            "Mariana",
            "Gustavo",
            "Natália",
            "Vinícius",
            "Carolina",
            "Leonardo",
            "Isabela",
            "Henrique",
            "Patrícia",
            "Eduardo",
            "Renata",
            "Marcos",
            "Vanessa",
            "Paulo",
            "Débora",
            "Ricardo",
            "Mônica",
            "Alexandre",
            "Cristina",
            "Fábio",
            "Adriana",
            "César",
            "Luciana",
            "Roberto",
            "Silvia",
            "Daniel",
            "Tatiana",
        ]

        sobrenomes = [
            "Silva",
            "Santos",
            "Oliveira",
            "Souza",
            "Rodrigues",
            "Ferreira",
            "Alves",
            "Pereira",
            "Lima",
            "Gomes",
            "Costa",
            "Ribeiro",
            "Martins",
            "Carvalho",
            "Almeida",
            "Lopes",
            "Soares",
            "Fernandes",
            "Vieira",
            "Barbosa",
            "Rocha",
            "Dias",
            "Monteiro",
            "Mendes",
            "Ramos",
            "Moreira",
            "Araújo",
            "Cardoso",
            "Nascimento",
            "Correia",
            "Teixeira",
            "Fonseca",
            "Pinto",
            "Moura",
            "Freitas",
        ]

        # Distribuição de roles: 70% alunos, 20% professores, 10% coordenadores
        roles_disponiveis = (
            ["aluno"] * 35  # 70% de 50 = 35
            + ["professor"] * 10  # 20% de 50 = 10
            + ["coordenador"] * 5  # 10% de 50 = 5
        )

        random.shuffle(roles_disponiveis)

        usuarios_criados = 0
        erros = 0

        for i in range(quantidade):
            try:
                # Gerar dados únicos
                nome = random.choice(nomes)
                sobrenome = random.choice(sobrenomes)
                numero = str(1000 + i).zfill(4)

                # Criar username único
                username = f"user{numero}"
                email = f"{nome.lower()}.{sobrenome.lower()}{numero}@iftest.edu.br"

                # Verificar se já existe
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f"Username {username} já existe, pulando...")
                    )
                    continue

                # Criar usuário
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=nome,
                    last_name=sobrenome,
                    password="123456",  # Senha padrão para teste
                )

                # Atribuir role
                role = roles_disponiveis[i % len(roles_disponiveis)]
                assign_role(user, role)

                # Criar perfil específico baseado na role
                if role == "aluno":
                    PerfilAluno.objects.create(user=user, situacao="Ativo")
                elif role in ["professor", "coordenador"]:
                    PerfilProfessor.objects.create(
                        user=user, registro_academico=f"REG{numero}"
                    )

                usuarios_criados += 1

                self.stdout.write(f"Criado: {username} - {nome} {sobrenome} ({role})")

            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f"Erro ao criar usuário {i+1}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nConcluído! {usuarios_criados} usuários criados com sucesso."
            )
        )

        if erros > 0:
            self.stdout.write(
                self.style.WARNING(f"{erros} erros encontrados durante a criação.")
            )

        # Exibir estatísticas
        total_usuarios = User.objects.count()
        total_alunos = PerfilAluno.objects.count()
        total_professores = PerfilProfessor.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nEstatísticas atuais:"
                f"\n- Total de usuários: {total_usuarios}"
                f"\n- Total de alunos: {total_alunos}"
                f"\n- Total de professores: {total_professores}"
            )
        )
