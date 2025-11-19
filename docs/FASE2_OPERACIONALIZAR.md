# Fase 2: Operacionalizar no Fluxo

## Objetivo
Garantir que o questionário padrão está disponível e funcionando corretamente no fluxo de criação de ciclos e resposta de avaliações.

## Checklist de Validação

### ✅ 1. Questionário Disponível
- [x] Comando seed executado com sucesso
- [x] Questionário "Avaliação Docente — Padrão" criado
- [x] 10 perguntas cadastradas com opções corretas
- [x] Questionário aparece em `CicloAvaliacaoForm` (filtrado como ativo e com perguntas)

### 🔄 2. Criar Ciclo de Teste

**Passos para teste manual:**

1. Acessar como admin/coordenador
2. Ir para "Gerenciar Ciclos"
3. Criar novo ciclo:
   - Nome: "Teste - Avaliação Docente 2025.1"
   - Período Letivo: selecionar período ativo
   - Questionário: **"Avaliação Docente — Padrão"** deve aparecer na lista
   - Data início: data atual
   - Data fim: +7 dias
   - Turmas: selecionar turmas de teste
4. Salvar ciclo

**Resultado esperado:**
- ✅ Ciclo criado com sucesso
- ✅ Questionário padrão selecionado
- ✅ Avaliações docentes criadas automaticamente para as turmas

### 🔄 3. Responder Avaliação (Aluno)

**Passos para teste manual:**

1. Acessar como aluno matriculado em turma do ciclo
2. Ir para "Avaliações Disponíveis"
3. Clicar em "Responder" em uma avaliação
4. Validar:
   - ✅ Todas as 10 perguntas aparecem
   - ✅ Cada pergunta tem 5 opções (Não atende, Insuficiente, Regular, Bom, Excelente)
   - ✅ Opções renderizadas como radio buttons
   - ✅ Campos marcados como obrigatórios
5. Responder avaliação selecionando opções
6. Submeter formulário

**Resultado esperado:**
- ✅ Avaliação salva com sucesso
- ✅ Respostas gravadas em `RespostaAvaliacao` com `valor_texto` = opção escolhida
- ✅ Aluno redirecionado para página de confirmação

### 🔄 4. Visualizar Respostas (Admin/Coordenador)

**Passos para teste manual:**

1. Acessar como admin/coordenador
2. Ir para "Relatórios de Avaliação"
3. Filtrar pelo ciclo de teste
4. Validar:
   - ✅ Respostas aparecem com texto da opção (ex: "Bom", "Excelente")
   - ✅ Contagem de respondentes está correta
   - ✅ Não há cálculos de média ainda (Fase 3)

## Comandos Úteis

### Verificar questionário no banco
```bash
python manage.py shell -c "from avaliacao_docente.models import QuestionarioAvaliacao; q = QuestionarioAvaliacao.objects.get(titulo='Avaliação Docente — Padrão'); print(f'ID: {q.id}'); print(f'Ativo: {q.ativo}'); print(f'Perguntas: {q.perguntas.count()}')"
```

### Listar ciclos usando o questionário padrão
```bash
python manage.py shell -c "from avaliacao_docente.models import CicloAvaliacao, QuestionarioAvaliacao; q = QuestionarioAvaliacao.objects.get(titulo='Avaliação Docente — Padrão'); ciclos = CicloAvaliacao.objects.filter(questionario=q); print(f'Ciclos usando questionário padrão: {ciclos.count()}'); [print(f'- {c.nome}') for c in ciclos]"
```

### Ver respostas de uma avaliação
```bash
python manage.py shell -c "from avaliacao_docente.models import AvaliacaoDocente, RespostaAvaliacao; av = AvaliacaoDocente.objects.first(); if av: respostas = RespostaAvaliacao.objects.filter(avaliacao=av); print(f'Avaliação: {av}'); print(f'Respostas: {respostas.count()}'); [print(f'- P{r.pergunta.id}: {r.valor_texto}') for r in respostas[:5]]"
```

## Melhorias Opcionais

### Pré-seleção do Questionário Padrão

Adicionar no `__init__` do `CicloAvaliacaoForm`:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    # ... código existente ...
    
    # Pré-selecionar questionário padrão se existir e não for edição
    if not self.instance.pk:
        try:
            questionario_padrao = QuestionarioAvaliacao.objects.get(
                titulo="Avaliação Docente — Padrão",
                ativo=True
            )
            self.fields["questionario"].initial = questionario_padrao.id
        except QuestionarioAvaliacao.DoesNotExist:
            pass
```

## Status Atual
🔄 **EM VALIDAÇÃO MANUAL**

Próximo: executar testes manuais acima e documentar resultados.

---

**Última atualização:** 13 de outubro de 2025
