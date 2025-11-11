/**
 * gerenciar-usuarios.js
 * Script específico para a página de gerenciamento de usuários
 * Sistema de Avaliação Docente SUAP
 */

// =================================
// VARIÁVEIS GLOBAIS
// =================================

let usuarioAtual = null;

// =================================
// FILTROS E BUSCA
// =================================

/**
 * Filtra a tabela de usuários com base nos critérios selecionados
 */
function filterTableUsuarios() {
  const searchFilter = document.getElementById('searchUsuario').value.toLowerCase();
  const roleFilter = document.getElementById('filterRole').value.toLowerCase();
  const statusFilter = document.getElementById('filterStatus').value.toLowerCase();

  const tableRows = document.querySelectorAll('.data-table tbody tr');
  let visibleCount = 0;

  tableRows.forEach(row => {
    const cells = row.querySelectorAll('td');

    // Verifica se a linha tem células (não é a linha "Nenhum usuário encontrado")
    if (cells.length > 1) {
      // Busca personalizada em múltiplos campos data-
      const searchMatch = !searchFilter ||
        (row.getAttribute('data-nome') || '').toLowerCase().includes(searchFilter) ||
        (row.getAttribute('data-email') || '').toLowerCase().includes(searchFilter) ||
        (row.getAttribute('data-matricula') || '').toLowerCase().includes(searchFilter);

      // Filtro de role - trata especialmente "sem-role"
      let roleMatch = !roleFilter;
      if (roleFilter) {
        const dataRole = (row.getAttribute('data-role') || '').toLowerCase();
        if (roleFilter === 'sem-role') {
          roleMatch = dataRole === 'sem role' || dataRole === '';
        } else {
          roleMatch = dataRole.includes(roleFilter);
        }
      }

      const statusMatch = !statusFilter || (row.getAttribute('data-status') || '').toLowerCase().includes(statusFilter);

      if (searchMatch && roleMatch && statusMatch) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    }
  });

  // Atualizar contador específico desta página
  updateUserCounter();

  // Lidar com empty state
  handleEmptyState();
}

/**
 * Atualiza o contador de usuários visíveis
 * @returns {number} Número de usuários visíveis
 */
function updateUserCounter() {
  const visibleRows = document.querySelectorAll('.data-table tbody tr:not([style*="display: none"])');
  let visibleCount = 0;

  visibleRows.forEach(row => {
    const cells = row.querySelectorAll('td');
    // Conta apenas linhas que têm células (não é a linha "Nenhum usuário encontrado")
    if (cells.length > 1) {
      visibleCount++;
    }
  });

  // Atualiza o contador no título
  const sectionTitle = document.querySelector('.section-header h2');
  if (sectionTitle) {
    sectionTitle.textContent = `👤 Lista de Usuários (${visibleCount})`;
  }

  return visibleCount;
}

/**
 * Lida com o estado vazio (quando não há resultados)
 */
function handleEmptyState() {
  const visibleCount = updateUserCounter(); // Reutiliza a contagem
  const emptyState = document.querySelector('.empty-state');

  // Mostra/esconde empty state baseado na contagem
  if (emptyState) {
    emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
  }

  // Remove mensagem temporária se existir
  const noResultsRow = document.querySelector('.no-results-row');
  if (noResultsRow) {
    noResultsRow.remove();
  }
}

/**
 * Limpa todos os filtros
 */
function clearFiltersUsuarios() {
  document.getElementById('searchUsuario').value = '';
  document.getElementById('filterRole').value = '';
  document.getElementById('filterStatus').value = '';
  filterTableUsuarios();
}

// =================================
// GERENCIAMENTO DE ROLES
// =================================

/**
 * Abre o modal para alterar a role de um usuário
 * @param {number} userId - ID do usuário
 * @param {string} nome - Nome completo do usuário
 * @param {string} matricula - Matrícula do usuário
 * @param {string} roleAtual - Role atual do usuário
 */
function alterarRole(userId, nome, matricula, roleAtual) {
  usuarioAtual = userId;

  // Atualizar informações do usuário
  document.getElementById('user-info').innerHTML = `
    <h4>Dados do Usuário</h4>
    <p><strong>Nome:</strong> ${nome}</p>
    <p><strong>Matrícula:</strong> ${matricula}</p>
    <p><strong>Role Atual:</strong> <span class="role-badge role-${roleAtual.toLowerCase()}">${roleAtual}</span></p>
  `;

  // Definir o ID do usuário no formulário
  document.getElementById('usuario-id').value = userId;

  // Limpar seleção anterior
  document.getElementById('role-select').value = '';

  // Mostrar modal usando a função global
  openModal('modal-overlay');
}

/**
 * Reseta a role para gerenciamento automático pelo SUAP
 * @param {number} userId - ID do usuário
 * @param {string} username - Username do usuário
 */
function resetarRoleAutomatica(userId, username) {
  if (confirm(`Tem certeza que deseja permitir que o SUAP volte a gerenciar automaticamente a role do usuário ${username}?\n\nIsso significa que a role será redefinida baseada no tipo de usuário no SUAP no próximo login.`)) {
    window.location.href = `/resetar-role-automatica/${userId}/`;
  }
}

// =================================
// INICIALIZAÇÃO
// =================================

/**
 * Inicializa os event listeners da página
 */
function initUsuariosPage() {
  // Adiciona event listeners aos campos de filtro
  const searchUsuario = document.getElementById('searchUsuario');
  const filterRole = document.getElementById('filterRole');
  const filterStatus = document.getElementById('filterStatus');

  if (searchUsuario) searchUsuario.addEventListener('input', filterTableUsuarios);
  if (filterRole) filterRole.addEventListener('change', filterTableUsuarios);
  if (filterStatus) filterStatus.addEventListener('change', filterTableUsuarios);

  // Inicializa o contador na carga da página
  updateUserCounter();

  console.log('✅ Página de gerenciamento de usuários inicializada');
}

// Auto-inicialização
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', initUsuariosPage);
}

// =================================
// EXPORTAR PARA ESCOPO GLOBAL
// =================================

if (typeof window !== 'undefined') {
  window.filterTableUsuarios = filterTableUsuarios;
  window.clearFiltersUsuarios = clearFiltersUsuarios;
  window.alterarRole = alterarRole;
  window.resetarRoleAutomatica = resetarRoleAutomatica;
  window.updateUserCounter = updateUserCounter;
}
