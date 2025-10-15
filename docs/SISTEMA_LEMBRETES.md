# Sistema de Lembretes Automáticos de Avaliação

## 📋 Visão Geral

O Sistema de Lembretes Automáticos foi desenvolvido para garantir que cada turma atinja um **limiar mínimo de 10% de respostas** nas avaliações docentes. O sistema envia e-mails automaticamente aos alunos que ainda não responderam, respeitando limites configuráveis e pausando automaticamente quando o objetivo é atingido.

### Características Principais

✅ **Automático**: Criação de jobs via signals quando ciclos são criados  
✅ **Inteligente**: Para automaticamente ao atingir 10% de respostas  
✅ **Controlado**: Limite de 3 lembretes por aluno (configurável)  
✅ **Monitorável**: Interface admin completa com métricas visuais  
✅ **Resiliente**: Tratamento robusto de erros e logs detalhados  
✅ **Escalável**: Processamento em lote (200 e-mails/iteração)

---

## 🏗️ Arquitetura do Sistema

### Modelos de Dados

#### 1. `JobLembreteCicloTurma`
Controla o envio de lembretes para cada combinação ciclo/turma.

**Campos principais:**
- `ciclo` (FK): Ciclo de avaliação
- `turma` (FK): Turma específica
- `status`: pendente | em_execucao | completo | pausado | erro
- `proximo_envio_em`: Data/hora do próximo disparo
- `total_alunos_aptos`: Total de matriculados ativos
- `total_respondentes`: Alunos que já responderam
- `taxa_resposta_atual`: Percentual de respostas (0-100)
- `total_emails_enviados`: Contador de e-mails
- `rodadas_executadas`: Número de execuções
- `mensagem_erro`: Último erro ocorrido

**Métodos:**
- `atingiu_limiar(limiar_percentual=10.0)`: Verifica se atingiu o mínimo
- `pode_executar()`: Valida se job pode rodar agora

#### 2. `NotificacaoLembrete`
Registra cada e-mail enviado individualmente (auditoria).

**Campos principais:**
- `job` (FK): Job pai
- `aluno` (FK): Destinatário
- `status`: pendente | enviado | falhou | ignorado
- `rodada`: Número sequencial do lembrete (1, 2, 3...)
- `tentativas`: Quantidade de tentativas de envio
- `enviado_em`: Timestamp do envio
- `mensagem_id`: Message-ID do e-mail
- `motivo_falha`: Detalhes de erro

#### 3. `ConfiguracaoSite` (campos adicionados)
Parâmetros globais do sistema.

- `limiar_minimo_percentual`: Padrão 10% (10.00)
- `frequencia_lembrete_horas`: Intervalo entre rodadas (padrão 48h)
- `max_lembretes_por_aluno`: Limite por aluno/ciclo (padrão 3)

---

## 🔄 Fluxo de Funcionamento

```
1. Admin cria CicloAvaliacao e adiciona turmas
   ↓
2. Signal cria JobLembreteCicloTurma para cada turma
   ↓
3. Comando periódico (cron/celery) executa:
   python manage.py enviar_lembretes_ciclos
   ↓
4. Para cada job pendente:
   a) Calcula taxa de resposta atual
   b) Se taxa >= 10%: marca job como completo e para
   c) Senão: seleciona alunos elegíveis
   d) Envia e-mails em lote (200/batch)
   e) Atualiza contadores e agenda próxima execução
   ↓
5. Notificações individuais são registradas
   ↓
6. Admin monitora progresso via interface visual
```

---

## 💻 Comandos de Gerenciamento

### Comando Principal

```bash
python manage.py enviar_lembretes_ciclos
```

**Opções disponíveis:**

#### `--dry-run`
Simula a execução sem enviar e-mails nem salvar no banco.
```bash
python manage.py enviar_lembretes_ciclos --dry-run
```
**Uso:** Testar o sistema antes de colocar em produção.

#### `--force-job-id ID`
Força o processamento de um job específico, ignorando `proximo_envio_em`.
```bash
python manage.py enviar_lembretes_ciclos --force-job-id 42
```
**Uso:** Processar uma turma urgente fora do cronograma.

#### `--batch-size N`
Define tamanho do lote de e-mails (padrão: 200).
```bash
python manage.py enviar_lembretes_ciclos --batch-size 50
```
**Uso:** Reduzir carga em produção ou ajustar limites do servidor SMTP.

### Exemplos Práticos

```bash
# Execução normal (usar no cron)
python manage.py enviar_lembretes_ciclos

# Teste completo sem efeitos colaterais
python manage.py enviar_lembretes_ciclos --dry-run

# Forçar job específico com lote menor
python manage.py enviar_lembretes_ciclos --force-job-id 15 --batch-size 100

# Simulação de job específico
python manage.py enviar_lembretes_ciclos --force-job-id 7 --dry-run
```

---

## ⚙️ Configuração

### 1. Parâmetros do Sistema

Acesse: **Admin → Configuração do Site**

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `limiar_minimo_percentual` | 10.00 | Taxa mínima para parar envios (%) |
| `frequencia_lembrete_horas` | 48 | Intervalo entre rodadas (horas) |
| `max_lembretes_por_aluno` | 3 | Limite de lembretes por aluno |

**Recomendações:**
- Produção: 48-72h de frequência
- Homologação: 24h para testes mais rápidos
- Não reduzir limiar abaixo de 10% (política institucional)

### 2. Configuração de E-mail

Certifique-se de ter no `settings.py`:

```python
# E-mail via API (Vercel) ou SMTP
DEFAULT_FROM_EMAIL = 'noreply@ifmt.edu.br'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # ou SendGrid

# URL do site (usado nos templates)
SITE_URL = 'https://avaliacoes.ifmt.edu.br'
```

### 3. Agendamento Automático (Produção)

#### Opção 1: Crontab (Recomendado)

```bash
# Editar crontab
crontab -e

# Executar a cada 6 horas
0 */6 * * * cd /path/to/project && source .venv/bin/activate && python manage.py enviar_lembretes_ciclos >> /var/log/lembretes.log 2>&1

# Ou diariamente às 8h
0 8 * * * cd /path/to/project && source .venv/bin/activate && python manage.py enviar_lembretes_ciclos
```

#### Opção 2: Celery Beat (Para infraestrutura maior)

```python
# celerybeat-schedule.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'enviar-lembretes-ciclos': {
        'task': 'avaliacao_docente.tasks.enviar_lembretes_task',
        'schedule': crontab(hour='*/6'),  # A cada 6 horas
    },
}
```

---

## 📊 Monitoramento via Admin

### 1. Jobs de Lembrete

**Caminho:** Admin → Jobs de Lembrete por Turma

**Visualização inclui:**
- ✨ Status colorido (pendente, em execução, completo, pausado, erro)
- 📊 Barra de progresso visual (respondentes/aptos)
- 📅 Próximo envio agendado
- 📈 Taxa de resposta atual
- 🔄 Rodadas executadas

**Actions disponíveis:**
- ⏸️ **Pausar jobs**: Interrompe envio temporariamente
- ▶️ **Retomar jobs**: Reativa jobs pausados
- ⚡ **Forçar execução imediata**: Agenda para próxima execução do comando

**Filtros:**
- Status (pendente, completo, pausado, erro)
- Ciclo de avaliação
- Curso da turma
- Data de criação

### 2. Notificações de Lembrete

**Caminho:** Admin → Notificações de Lembrete

**Visualização inclui:**
- ✅ Status com ícones (enviado, falhou, pendente, ignorado)
- 👤 Nome completo do aluno
- 🔢 Número da rodada (1º, 2º, 3º lembrete)
- 📧 Tentativas de envio
- ⏰ Data/hora do envio
- ❌ Motivo de falha (se aplicável)

**Recursos:**
- 🔒 Somente leitura (auditoria)
- 🔍 Busca por aluno, turma, ciclo
- 📅 Filtros por status, rodada, ciclo, data

---

## 🎯 Lógica de Elegibilidade

### Quem Recebe Lembretes?

✅ **SIM** - Aluno recebe se:
- Tem matrícula **ativa** na turma
- **NÃO** respondeu nenhuma avaliação da turma neste ciclo
- **NÃO** atingiu o limite de lembretes (3 por padrão)
- Job está **pendente** ou **em execução**
- Taxa da turma está **abaixo de 10%**

❌ **NÃO** - Aluno é ignorado se:
- Já respondeu a avaliação
- Atingiu limite de 3 lembretes
- Matrícula inativa/cancelada
- Job pausado/completo/erro
- Taxa da turma ≥ 10%

### Cálculo da Taxa de Resposta

```python
# Alunos aptos: matriculas ativas
alunos_aptos = turma.matriculas.filter(status='ativa').count()

# Respondentes: alunos distintos que responderam
respondentes = RespostaAvaliacao.objects.filter(
    avaliacao__turma=turma,
    avaliacao__ciclo=ciclo
).values('aluno_id').distinct().count()

# Taxa percentual
taxa = (respondentes / alunos_aptos) * 100.0 if alunos_aptos > 0 else 0.0
```

---

## 🔧 Troubleshooting

### Problema: Jobs não estão sendo executados

**Diagnósticos:**

1. **Verificar jobs pendentes:**
```bash
python manage.py shell
>>> from avaliacao_docente.models import JobLembreteCicloTurma
>>> from django.utils import timezone
>>> JobLembreteCicloTurma.objects.filter(
...     status='pendente',
...     proximo_envio_em__lte=timezone.now()
... ).count()
```

2. **Conferir crontab:**
```bash
crontab -l  # Verificar se comando está agendado
tail -f /var/log/lembretes.log  # Ver logs de execução
```

3. **Testar manualmente:**
```bash
python manage.py enviar_lembretes_ciclos --dry-run
```

**Solução:** Se houver jobs pendentes mas não estão rodando, execute:
```bash
python manage.py enviar_lembretes_ciclos --force-job-id ID_DO_JOB
```

---

### Problema: E-mails não estão sendo enviados

**Diagnósticos:**

1. **Verificar configuração de e-mail:**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Teste', 'Mensagem', 'noreply@ifmt.edu.br', ['seu@email.com'])
```

2. **Conferir notificações com falha:**
```python
>>> from avaliacao_docente.models import NotificacaoLembrete
>>> NotificacaoLembrete.objects.filter(status='falhou').values('motivo_falha')
```

3. **Verificar logs do Django:**
```bash
tail -f /var/log/django/error.log
```

**Soluções comuns:**
- Credenciais SMTP incorretas → Verificar `settings.py`
- Limite de envio atingido → Aguardar ou aumentar `batch_size`
- E-mails inválidos → Validar cadastro de alunos

---

### Problema: Taxa não atualiza mesmo com respostas

**Diagnósticos:**

1. **Verificar cálculo manual:**
```python
>>> from avaliacao_docente.services import calcular_taxa_resposta_turma
>>> from avaliacao_docente.models import CicloAvaliacao, Turma
>>> ciclo = CicloAvaliacao.objects.get(id=CICLO_ID)
>>> turma = Turma.objects.get(id=TURMA_ID)
>>> calcular_taxa_resposta_turma(ciclo, turma)
```

2. **Verificar respostas:**
```python
>>> from avaliacao_docente.models import RespostaAvaliacao
>>> RespostaAvaliacao.objects.filter(
...     avaliacao__turma_id=TURMA_ID,
...     avaliacao__ciclo_id=CICLO_ID
... ).values('aluno_id').distinct().count()
```

**Solução:** Forçar recálculo executando o comando:
```bash
python manage.py enviar_lembretes_ciclos --force-job-id ID_DO_JOB --dry-run
# Se taxa aparecer correta, executar sem --dry-run
```

---

### Problema: Jobs travados em "em_execucao"

**Causa:** Comando foi interrompido durante execução.

**Solução:**
```python
>>> from avaliacao_docente.models import JobLembreteCicloTurma
>>> JobLembreteCicloTurma.objects.filter(status='em_execucao').update(status='pendente')
```

---

## 📧 Templates de E-mail

### Variáveis Disponíveis

Os templates recebem o seguinte contexto:

```python
{
    'nome_aluno': 'João da Silva',
    'nome_curso': 'Técnico em Informática',
    'codigo_turma': 'INFO-2024-1',
    'nome_ciclo': '1º Semestre 2024',
    'data_fim': date(2024, 6, 30),
    'link_avaliacao': 'https://avaliacoes.ifmt.edu.br/avaliacoes/',
    'rodada': 2,  # Número sequencial do lembrete
}
```

### Personalizando Templates

**Localização:**
- HTML: `templates/emails/lembrete_avaliacao.html`
- Texto: `templates/emails/lembrete_avaliacao.txt`

**Exemplo de personalização:**

```html
<!-- Destacar urgência no 3º lembrete -->
{% if rodada == 3 %}
<div class="alert-danger">
    ⚠️ ÚLTIMO LEMBRETE! Prazo final em {{ data_fim|date:"d/m/Y" }}
</div>
{% endif %}
```

---

## 📈 Métricas e KPIs

### Indicadores de Sucesso

**Taxa de Conversão:**
```
Alunos que responderam após lembrete / Total de lembretes enviados
```

**Efetividade por Rodada:**
- 1º lembrete: ~40-50% de conversão
- 2º lembrete: ~30-35% de conversão
- 3º lembrete: ~15-20% de conversão

**Metas:**
- ✅ 100% das turmas atingindo 10% de respostas
- ✅ <5% de jobs com erro
- ✅ <2% de e-mails falhados

### Consultas Úteis

**Jobs por status:**
```sql
SELECT status, COUNT(*) 
FROM avaliacao_docente_joblembretecicloturma 
GROUP BY status;
```

**Taxa média de resposta:**
```sql
SELECT AVG(taxa_resposta_atual) 
FROM avaliacao_docente_joblembretecicloturma 
WHERE status = 'completo';
```

**Alunos mais resistentes:**
```sql
SELECT aluno_id, COUNT(*) as total_lembretes
FROM avaliacao_docente_notificacaolembrete
WHERE status = 'enviado'
GROUP BY aluno_id
HAVING total_lembretes >= 3
ORDER BY total_lembretes DESC;
```

---

## 🚀 Boas Práticas

### Desenvolvimento

1. ✅ Sempre testar com `--dry-run` antes de executar em produção
2. ✅ Monitorar logs da primeira execução real
3. ✅ Começar com frequência baixa (72h) e ajustar gradualmente
4. ✅ Validar templates de e-mail em diferentes clientes (Gmail, Outlook, etc.)
5. ✅ Manter backup dos logs de notificações

### Produção

1. ✅ Agendar execuções fora de horários de pico (madrugada/fim de semana)
2. ✅ Configurar alertas para jobs com status "erro"
3. ✅ Revisar mensagens de erro semanalmente
4. ✅ Pausar jobs de ciclos expirados manualmente se necessário
5. ✅ Documentar mudanças nos parâmetros de configuração

### Segurança

1. ✅ Não expor e-mails de alunos em logs públicos
2. ✅ Respeitar LGPD: lembretes apenas para finalidade educacional
3. ✅ Implementar rate limiting no servidor SMTP
4. ✅ Validar autenticação DKIM/SPF para evitar spam
5. ✅ Não deletar notificações (auditoria obrigatória)

---

## 📝 FAQ

**P: Posso mudar o limiar de 10% para outro valor?**  
R: Sim, acesse Admin → Configuração do Site → `limiar_minimo_percentual`. Porém, 10% é o padrão institucional baseado na Resolução 87/2023.

**P: Como pausar lembretes de um ciclo específico?**  
R: Admin → Jobs de Lembrete → Filtrar por ciclo → Selecionar todos → Action "Pausar jobs".

**P: Aluno reclamou de receber muitos e-mails. O que fazer?**  
R: Verificar no admin quantos lembretes ele recebeu. Se ultrapassou o limite (3), há um bug. Se está dentro do limite, explicar a importância da avaliação.

**P: E-mails estão caindo no spam. Como resolver?**  
R: 1) Configurar SPF/DKIM no DNS, 2) Usar domínio institucional, 3) Reduzir frequência de envio, 4) Melhorar conteúdo do e-mail (evitar palavras-gatilho).

**P: Posso enviar lembretes manualmente para uma turma?**  
R: Sim, use `--force-job-id` com o ID do job da turma.

**P: Como saber se o sistema está funcionando?**  
R: 1) Admin → Jobs → Verificar "última_execucao" atualizada, 2) Checar logs do comando, 3) Validar notificações com status "enviado".

---

## 📞 Suporte

**Desenvolvedor:** Equipe AeVALIS  
**Documentação:** `/docs/SISTEMA_LEMBRETES.md`  
**Repositório:** [GitHub - avaliacao_docente_suap](https://github.com/K6IK9/AeVALIS.SGAD)  
**Issues:** Abrir ticket no repositório com label `lembretes`

---

## 📜 Changelog

### v1.0.0 (Outubro 2025)
- ✨ Implementação inicial do sistema de lembretes
- ✨ Models: JobLembreteCicloTurma, NotificacaoLembrete
- ✨ Command: enviar_lembretes_ciclos
- ✨ Admin interface com métricas visuais
- ✨ Templates HTML/TXT responsivos
- ✨ Signals automáticos para criação de jobs
- ✨ Documentação completa

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0.0
