# Interface de Configuração de Lembretes

## 📍 Localização

**URL:** `/admin/configuracao/`  
**Menu:** Hub de Administração → ⚙️ Configuração do Site

---

## 🎨 Nova Seção: Sistema de Lembretes Automáticos

A página de configuração agora inclui uma seção dedicada aos lembretes automáticos com os seguintes campos editáveis:

### Campos Configuráveis

#### 1. **Limiar Mínimo de Respostas (%)**
- **Campo:** `limiar_minimo_percentual`
- **Tipo:** Número decimal (0.00 - 100.00)
- **Padrão:** 10.00%
- **Badge:** "Recomendado: 10%"
- **Descrição:** Percentual mínimo de respostas para parar o envio de lembretes automaticamente
- **Validação:** Min: 0, Max: 100, Step: 0.01

#### 2. **Frequência de Lembretes (horas)**
- **Campo:** `frequencia_lembrete_horas`
- **Tipo:** Número inteiro (≥1)
- **Padrão:** 48h
- **Badge:** "Recomendado: 48h"
- **Descrição:** Intervalo em horas entre cada rodada de lembretes
- **Validação:** Min: 1

#### 3. **Máximo de Lembretes por Aluno**
- **Campo:** `max_lembretes_por_aluno`
- **Tipo:** Número inteiro (1-10)
- **Padrão:** 3
- **Badge:** "Recomendado: 3"
- **Descrição:** Número máximo de lembretes que um aluno pode receber por ciclo
- **Validação:** Min: 1, Max: 10

### Informações Adicionais

**Box Informativo:**
> ℹ️ **Informação:** O tamanho do lote de envio (padrão: 200 e-mails/iteração) é configurado via parâmetro `--batch-size` no comando `enviar_lembretes_ciclos`. Para mais detalhes, consulte a documentação do sistema de lembretes.

**Links Úteis:**
- 📖 Sistema de Lembretes Automáticos
- 🔍 Monitorar Jobs de Lembrete (link direto para Django Admin)

---

## 🎯 Fluxo de Uso

1. **Acessar:** Admin Hub → Configuração do Site
2. **Rolar até:** Seção "📧 Sistema de Lembretes Automáticos"
3. **Ajustar valores** conforme necessário:
   - Limiar: Ex: 15% para turmas maiores
   - Frequência: Ex: 72h para espaçar mais
   - Max lembretes: Ex: 5 para campanhas intensivas
4. **Salvar Configurações**
5. **Verificar:** Mensagem de sucesso "Configurações do site atualizadas com sucesso!"

---

## 🔄 Impacto das Mudanças

### ⚡ Efeito Imediato
As configurações são aplicadas na **próxima execução** do comando `enviar_lembretes_ciclos`.

### 🎯 Jobs Existentes
- **Limiar:** Jobs pendentes verificam o novo limiar na próxima rodada
- **Frequência:** Próximo envio é recalculado com a nova frequência
- **Max lembretes:** Aplicado imediatamente na seleção de alunos elegíveis

### 📊 Exemplo de Cenário

**Antes:**
```
Limiar: 10%
Frequência: 48h
Max: 3
```

**Alteração para:**
```
Limiar: 15%
Frequência: 24h
Max: 5
```

**Resultado:**
- Turmas precisam atingir 15% para parar (mais exigente)
- Lembretes enviados a cada 24h (mais frequente)
- Alunos podem receber até 5 lembretes (mais chances)

---

## 🎨 Design

### Badges Informativos
Cada campo exibe um badge com a recomendação padrão:
- 🔵 Azul claro: `Recomendado: Xh` ou `Recomendado: X%`

### Validação Visual
- ✅ Campo válido: Borda azul ao focar
- ❌ Campo inválido: Alert vermelho com mensagem de erro

### Organização
- Separador visual (linha horizontal) entre seções
- Ícones: 📧 para lembretes, ⚙️ para configurações gerais
- Barras coloridas à esquerda dos títulos (gradiente roxo)

---

## 🧪 Testando as Configurações

### Teste Rápido (Dry Run)
```bash
python manage.py enviar_lembretes_ciclos --dry-run
```

Verifique na saída:
```
⚙️  Configurações:
   - Limiar mínimo: 15.00%  ← Novo valor
   - Frequência: 24h         ← Novo valor
   - Max lembretes/aluno: 5  ← Novo valor
```

### Validação de Valores

**Limiar:**
- ❌ Inválido: Valores negativos ou > 100
- ✅ Válido: 0.00 a 100.00 (com 2 decimais)

**Frequência:**
- ❌ Inválido: 0 ou valores negativos
- ✅ Válido: Qualquer inteiro ≥ 1

**Max Lembretes:**
- ❌ Inválido: 0, negativos ou > 10
- ✅ Válido: 1 a 10

---

## 📱 Responsividade

A interface é totalmente responsiva:
- **Desktop:** Campos ocupam largura completa com espaçamento adequado
- **Tablet:** Layout mantém-se confortável
- **Mobile:** Formulário empilha verticalmente

---

## 🔒 Permissões

**Acesso restrito a:**
- Administradores (role: `admin`)
- Coordenadores (role: `coordenador`)

**Verificação:** Decorator `@login_required` + `check_user_permission()`

---

## ✅ Checklist de Atualização

- [x] Formulário atualizado (`ConfiguracaoSiteForm`)
- [x] Template atualizado (`gerenciar_configuracao.html`)
- [x] CSS melhorado com badges e validação visual
- [x] Links para monitoramento (Jobs Admin)
- [x] Box informativo sobre batch-size
- [x] Validações de campo (min/max)
- [x] Help texts descritivos
- [x] Design consistente com o restante do sistema

---

**Atualizado em:** 16 de outubro de 2025  
**Versão:** 1.0.0
