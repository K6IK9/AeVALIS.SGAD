# Padronização dos Filtros - Páginas de Gerenciamento

## Páginas Padronizadas ✅

### 1. gerenciar_roles.html
- **Status**: ✅ Padronizada (padrão de referência)
- **Filtros**: Busca por nome/matrícula + Filtro por role
- **Botões**: 🔍 Pesquisar + Limpar Filtros
- **Estrutura**: `filters-section` > `filter-row` > `filter-group`
- **JavaScript**: `aplicarFiltros()` + `limparFiltros()`

### 2. gerenciar_usuarios.html  
- **Status**: ✅ Padronizada
- **Filtros**: Busca por nome/email/matrícula + Filtro por função + Filtro por status
- **Botões**: 🔍 Pesquisar + Limpar Filtros
- **Estrutura**: `filters-section` com estrutura padronizada
- **JavaScript**: `limparFiltros()` implementada

### 3. gerenciar_turmas.html
- **Status**: ✅ Padronizada 
- **Filtros**: Período letivo + Disciplina + Professor
- **Botões**: 🔍 Pesquisar + Limpar Filtros
- **Estrutura**: `filters-section` padronizada
- **JavaScript**: `aplicarFiltros()` + `limparFiltros()` + remoção de código duplicado

### 4. gerenciar_alunos_turma.html
- **Status**: ✅ Padronizada
- **Filtros**: Busca por nome/matrícula/email
- **Botões**: 🔍 Pesquisar + Limpar Filtros
- **Estrutura**: `filters-section` padronizada
- **JavaScript**: `limparFiltros()` implementada

## Estrutura Padrão Implementada

### HTML
```html
<div class="filters-section">
    <h3 class="filters-title">Filtros e Busca</h3>
    <form method="get" id="filtros-form">
        <div class="filter-row">
            <div class="filter-group">
                <label for="campo">Label do Campo:</label>
                <input/select class="form-control">
            </div>
            <div class="filter-group">
                <button type="submit" class="btn-filter">🔍 Pesquisar</button>
            </div>
            <div class="filter-group">
                <button type="button" class="btn-filter" onclick="limparFiltros()">Limpar Filtros</button>
            </div>
        </div>
    </form>
</div>
```

### CSS Classes Utilizadas
- `.filters-section`: Container principal dos filtros
- `.filters-title`: Título da seção de filtros
- `.filter-row`: Linha que contém os grupos de filtros
- `.filter-group`: Grupo individual de cada filtro/botão
- `.form-control`: Classes para inputs e selects
- `.btn-filter`: Classe para botões de filtro

### JavaScript Padrão
```javascript
// Função para aplicar filtros (quando necessário)
function aplicarFiltros() {
    document.getElementById('filtros-form').submit();
}

// Função para limpar filtros (obrigatória)
function limparFiltros() {
    // Limpar todos os campos do formulário
    document.getElementById('campo1').value = '';
    document.getElementById('campo2').value = '';
    // Submeter formulário vazio
    document.getElementById('filtros-form').submit();
}
```

## Páginas que NÃO Precisam de Filtros

### gerenciar_categorias.html
- **Motivo**: Apenas formulário de criação/edição, sem listagem que justifique filtros
- **Conteúdo**: Formulário simples para nome, ordem e descrição

### gerenciar_cursos.html
- **Status**: ⚠️ Precisa verificação
- **Motivo**: Pode precisar de filtros se tiver listagem extensa

### gerenciar_disciplinas.html  
- **Status**: ⚠️ Precisa verificação
- **Motivo**: Pode precisar de filtros por curso

### gerenciar_periodos.html
- **Status**: ⚠️ Precisa verificação
- **Motivo**: Pode precisar de filtros por data/status

### gerenciar_questionarios.html
- **Status**: ⚠️ Precisa verificação  
- **Motivo**: Pode precisar de filtros por categoria/status

### gerenciar_ciclos.html
- **Status**: ⚠️ Precisa verificação
- **Motivo**: Pode precisar de filtros por período/status

## Benefícios da Padronização

1. **Consistência Visual**: Todas as páginas têm a mesma aparência e comportamento
2. **Experiência do Usuário**: Usuários sabem exatamente onde encontrar filtros e como usá-los  
3. **Manutenibilidade**: Código mais fácil de manter e atualizar
4. **Acessibilidade**: Estrutura semântica consistente
5. **Funcionalidade**: Botão "Limpar Filtros" sempre disponível

## Próximos Passos

1. ✅ Verificar páginas restantes que podem precisar de filtros
2. ✅ Implementar filtros onde necessário usando a estrutura padrão
3. ✅ Testar todas as funcionalidades
4. ✅ Documentar exemplos específicos para cada tipo de filtro

## Observações Técnicas

- **IDs únicos**: Cada campo deve ter ID único para funcionamento do JavaScript
- **Form method="get"**: Para que filtros sejam mantidos na URL
- **Preservação de valores**: `value="{{ request.GET.campo }}"` para manter filtros após submissão
- **Classes CSS**: Seguir estrutura `.filters-section` para herdar estilos corretos
- **JavaScript**: Sempre implementar `limparFiltros()` para reset completo
