# Gerenciamento de Roles Manuais vs Automáticas

## Problema Resolvido

Anteriormente, quando um administrador alterava manualmente a role de um usuário no sistema, essa alteração era perdida no próximo login do usuário via SUAP, pois a pipeline de autenticação sempre redefinia as roles baseadas no `tipo_usuario` retornado pelo SUAP.

## Solução Implementada

Foi criado um sistema de flags que permite marcar quando uma role foi definida manualmente, evitando que seja sobrescrita automaticamente.

### Como Funciona

1. **Alteração Manual**: Quando um administrador altera a role de um usuário através da interface de gerenciamento, uma flag `role_manually_changed` é definida nos dados extras do usuário no social auth.

2. **Verificação na Pipeline**: A pipeline de autenticação (`auth_pipeline.py`) verifica se existe essa flag antes de aplicar mudanças automáticas. Se a flag existir, a role não é alterada.

3. **Indicação Visual**: No template de gerenciamento de roles, usuários com roles definidas manualmente são identificados com um ícone de cadeado (🔒).

4. **Reset de Flag**: Administradores podem resetar a flag, permitindo que o SUAP volte a gerenciar automaticamente a role do usuário.

### Funcionalidades Disponíveis

#### Interface Web
- **Visualização**: Usuários com roles manuais são identificados com ícone 🔒
- **Alteração**: Toda alteração de role via interface marca automaticamente como manual
- **Reset**: Botão "🔓 Resetar Auto" disponível apenas para administradores

#### Comando de Gerenciamento
```bash
# Listar usuários com flags manuais
python manage.py manage_role_flags --list

# Remover todas as flags manuais (simulação)
python manage.py manage_role_flags --reset-all --dry-run

# Remover todas as flags manuais (aplicar)
python manage.py manage_role_flags --reset-all

# Remover flag de usuário específico
python manage.py manage_role_flags --reset-user <username>

# Definir flag para usuário específico
python manage.py manage_role_flags --set-user <username>
```

### Funções Utilitárias

#### `avaliacao_docente.utils`

- `mark_role_manually_changed(user)`: Marca role como alterada manualmente
- `reset_role_manual_flag(user)`: Remove flag manual
- `is_role_manually_changed(user)`: Verifica se role foi alterada manualmente

### Fluxo de Funcionamento

1. **Usuário faz login inicial**: Role é definida automaticamente pelo SUAP
2. **Admin altera role**: Flag manual é ativada automaticamente
3. **Próximos logins**: Role não é alterada (respeitando a definição manual)
4. **Reset da flag**: Admin pode remover a flag, voltando ao comportamento automático

### Exceções

- **Administradores**: Roles de admin nunca são alteradas automaticamente
- **Primeiro login**: Flag manual não impede a definição inicial da role
- **Usuários sem SUAP**: Sistema funciona normalmente para usuários locais

### Segurança

- Apenas administradores podem resetar flags manuais
- A interface mostra claramente quais roles são manuais
- Logs são gerados para mudanças importantes

## Casos de Uso

1. **Professor vira Coordenador**: Admin pode alterar manualmente e a mudança será mantida
2. **Aluno vira Monitor**: Pode ter role de professor mantida mesmo sendo aluno no SUAP
3. **Correção de Erro**: Admin pode resetar flag para voltar ao comportamento automático
4. **Auditoria**: Comando permite listar todos os usuários com roles manuais
