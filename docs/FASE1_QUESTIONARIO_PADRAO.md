# Fase 1: Questionário Padrão (CONCLUÍDA)

## Objetivo
Criar o questionário padrão de avaliação docente com 10 perguntas, todas com o mesmo formato de resposta baseado na escala: Não atende (0,00), Insuficiente (0,25), Regular (0,50), Bom (0,75), Excelente (1,00).

## O que foi implementado

### 1. Comando de Seed Idempotente
**Arquivo:** `avaliacao_docente/management/commands/seed_questionario_padrao.py`

- Cria/atualiza categoria "Atividades de Ensino / Atuação Pedagógica"
- Cria/atualiza questionário "Avaliação Docente — Padrão"
- Cadastra as 10 perguntas obrigatórias com tipo `multipla_escolha`
- Execução idempotente: pode ser rodado múltiplas vezes sem duplicar dados

**Uso:**
```bash
python manage.py seed_questionario_padrao
```

### 2. Correções nos Forms
**Arquivo:** `avaliacao_docente/forms.py`

- Ajustado `CursoForm` e `DisciplinaForm` para evitar execução de queries do manager `non_admin` durante importação do módulo
- Movido `queryset=PerfilProfessor.non_admin.all()` para o método `__init__` dos forms
- Isso resolve erro de circular import durante startup do Django

### 3. Estrutura das Perguntas

**Categoria:** Atividades de Ensino / Atuação Pedagógica

**Questionário:** Avaliação Docente — Padrão

**10 Perguntas (todas obrigatórias, tipo multipla_escolha):**

1. Informa o programa/plano de ensino e deixa claro o objetivo da disciplina.
2. Demonstra clareza e objetividade na explicação dos conteúdos da disciplina.
3. Relaciona os conceitos teóricos com a prática do cotidiano.
4. Indica fontes de consulta (sites, livros, artigos, etc.) relacionadas à disciplina.
5. Utiliza recursos didáticos de forma que promova o aprendizado.
6. Proporciona oportunidades de questionamentos e esclarecimentos de dúvidas relevantes.
7. Apresenta previamente os critérios de avaliação aos alunos.
8. Estabelece uma relação de respeito com os estudantes.
9. Estimula os alunos a relacionar o conhecimento com outras disciplinas.
10. Exige nas avaliações de aprendizagem os conteúdos desenvolvidos.

**Opções de resposta (idênticas para todas as perguntas):**
- Não atende
- Insuficiente
- Regular
- Bom
- Excelente

### 4. Fluxo de Resposta

**Form:** `RespostaAvaliacaoForm` (já existente em `forms.py`)

- Suporta tipo `multipla_escolha` com rendering de radio buttons
- Salva a opção escolhida em `RespostaAvaliacao.valor_texto`
- Pronto para uso sem modificações adicionais

## Validação

Executado comando de validação:
```bash
python manage.py shell -c "from avaliacao_docente.models import QuestionarioAvaliacao, QuestionarioPergunta; q = QuestionarioAvaliacao.objects.get(titulo='Avaliação Docente — Padrão'); perguntas = QuestionarioPergunta.objects.filter(questionario=q).order_by('ordem_no_questionario'); print(f'Total: {perguntas.count()}'); [print(f'{p.ordem_no_questionario}. {p.pergunta.enunciado[:60]}... | Opções: {len(p.pergunta.opcoes_multipla_escolha)}') for p in perguntas]"
```

**Resultado:** ✅ 10 perguntas cadastradas corretamente com 5 opções cada

## Status
✅ **FASE 1 CONCLUÍDA**

## Próxima Fase
**Fase 2:** Operacionalizar no fluxo
- Disponibilizar questionário para uso em ciclos
- Validar que alunos conseguem responder
- Opcional: pré-selecionar o questionário padrão ao criar ciclos

---

**Data de conclusão:** 13 de outubro de 2025
