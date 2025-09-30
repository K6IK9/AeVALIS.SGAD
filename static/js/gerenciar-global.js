/**
 * gerenciar-global.js
 * Arquivo JavaScript global para funcionalidades comuns das páginas de gerenciamento
 * Funcionalidades incluídas:
 * - Drag scroll em tabelas
 * - Gerenciamento de modais
 * - Filtros e busca
 * - Dicas de scroll
 * - Utilitários comuns
 */

// =================================
// DRAG SCROLL FUNCTIONALITY
// =================================

/**
 * Habilita a funcionalidade de arrastar para fazer scroll em tabelas
 * Funciona tanto em desktop (mouse) quanto em mobile (touch)
 */
function enableDragScroll() {
  const tableContainer = document.querySelector('.table-responsive');
  if (!tableContainer) return;

  let isDown = false;
  let startX;
  let scrollLeft;

  // Mouse events
  tableContainer.addEventListener('mousedown', (e) => {
    // Evitar drag em elementos interativos
    if (e.target.tagName === 'INPUT' ||
      e.target.tagName === 'BUTTON' ||
      e.target.tagName === 'A' ||
      e.target.closest('button') ||
      e.target.closest('a')) {
      return;
    }

    isDown = true;
    tableContainer.classList.add('grabbing');
    startX = e.pageX - tableContainer.offsetLeft;
    scrollLeft = tableContainer.scrollLeft;
    e.preventDefault();
  });

  tableContainer.addEventListener('mouseleave', () => {
    isDown = false;
    tableContainer.classList.remove('grabbing');
  });

  tableContainer.addEventListener('mouseup', () => {
    isDown = false;
    tableContainer.classList.remove('grabbing');
  });

  tableContainer.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - tableContainer.offsetLeft;
    const walk = (x - startX) * 2;
    tableContainer.scrollLeft = scrollLeft - walk;
  });

  // Touch events for mobile
  tableContainer.addEventListener('touchstart', (e) => {
    if (e.target.tagName === 'INPUT' ||
      e.target.tagName === 'BUTTON' ||
      e.target.tagName === 'A') {
      return;
    }

    isDown = true;
    startX = e.touches[0].pageX - tableContainer.offsetLeft;
    scrollLeft = tableContainer.scrollLeft;
  });

  tableContainer.addEventListener('touchmove', (e) => {
    if (!isDown) return;
    const x = e.touches[0].pageX - tableContainer.offsetLeft;
    const walk = (x - startX) * 2;
    tableContainer.scrollLeft = scrollLeft - walk;
  });

  tableContainer.addEventListener('touchend', () => {
    isDown = false;
  });

  // Scroll smooth behavior
  tableContainer.style.scrollBehavior = 'auto';
}

// =================================
// MODAL MANAGEMENT
// =================================

/**
 * Abre um modal pelo ID
 * @param {string} modalId - ID do modal a ser aberto
 */
function openModal(modalId) {
  if (typeof document !== 'undefined') {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'flex';
      modal.classList.add('show', 'active');
      document.body.style.overflow = 'hidden';
    }
  }
}

/**
 * Fecha um modal pelo ID
 * @param {string} modalId - ID do modal a ser fechado
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'none';
    modal.classList.remove('show', 'active');
    document.body.style.overflow = '';
  }
}

/**
 * Configura event listeners para modais
 * - Fechar ao clicar fora
 * - Fechar com tecla Escape
 */
function setupModalEvents() {
  // Fechar modal ao clicar fora
  if (typeof document !== 'undefined') {
    document.addEventListener('click', function (e) {
      if (e.target.classList.contains('modal') ||
        e.target.classList.contains('modal-overlay')) {
        const modal = e.target;
        closeModal(modal.id);
      }
    });

    // Fechar modal com tecla Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show, .modal.active, .modal-overlay.active');
        if (openModal) {
          closeModal(openModal.id);
        }
      }
    });
  }
}

// =================================
// FILTROS E BUSCA
// =================================

/**
 * Configura busca automática com delay
 * @param {string} inputId - ID do campo de busca
 * @param {Function} callback - Função a ser executada na busca
 * @param {number} delay - Delay em ms (padrão: 500ms)
 */
function setupAutoSearch(inputId, callback, delay = 500) {
  if (typeof document !== 'undefined') {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;

    let searchTimeout;
    searchInput.addEventListener('input', function () {
      if (typeof clearTimeout !== 'undefined' && typeof setTimeout !== 'undefined') {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          callback();
        }, delay);
      }
    });
  }
}

/**
 * Função genérica para aplicar filtros via submit do formulário
 */
function aplicarFiltros() {
  if (typeof document !== 'undefined') {
    const form = document.getElementById('filtros-form');
    if (form) {
      form.submit();
    }
  }
}

/**
 * Função genérica para limpar todos os filtros de um formulário
 * @param {Array} fieldIds - Array com IDs dos campos a serem limpos
 * @param {string} formId - ID do formulário (padrão: 'filtros-form')
 */
function limparFiltros(fieldIds = [], formId = 'filtros-form') {
  // Limpar campos específicos se fornecidos
  if (typeof document !== 'undefined') {
    fieldIds.forEach(fieldId => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.value = '';
      }
    });

    // Se não foram especificados campos, limpar todos os inputs e selects do formulário
    if (fieldIds.length === 0) {
      const form = document.getElementById(formId);
      if (form) {
        const inputs = form.querySelectorAll('input[type="text"], input[type="search"], select');
        inputs.forEach(input => {
          input.value = '';
        });
      }
    }

    // Submeter formulário
    const form = document.getElementById(formId);
    if (form) {
      form.submit();
    }
  }
}

/**
 * Filtra uma tabela em tempo real baseado em critérios
 * @param {Object} filters - Objeto com os filtros {fieldId: attributeName}
 * @param {string} tableSelector - Seletor da tabela (padrão: '.data-table tbody tr')
 * @param {string} counterId - ID do elemento contador (opcional)
 */
function filterTable(filters = {}, tableSelector = '.data-table tbody tr', counterId = null) {
  if (typeof document !== 'undefined') {
    const rows = document.querySelectorAll(tableSelector);
    let visibleCount = 0;

    rows.forEach(row => {
      let shouldShow = true;

      // Aplicar cada filtro
      Object.entries(filters).forEach(([fieldId, attribute]) => {
        const filterValue = document.getElementById(fieldId)?.value.toLowerCase() || '';
        if (!filterValue) return;

        let rowValue = '';
        if (attribute.startsWith('data-')) {
          // Para atributos data-*
          rowValue = row.getAttribute(attribute) || '';
        } else {
          // Para texto dentro de células
          const cells = row.querySelectorAll('td');
          const cellIndex = Number(attribute);
          if (Number.isInteger(cellIndex) && cellIndex >= 0 && cellIndex < cells.length) {
            rowValue = cells[cellIndex].textContent || '';
          } else {
            // Buscar em todo o texto da linha
            rowValue = row.textContent || '';
          }
        }

        if (!rowValue.toLowerCase().includes(filterValue)) {
          shouldShow = false;
        }
      });

      // Mostrar/esconder linha
      row.style.display = shouldShow ? '' : 'none';
      if (shouldShow) visibleCount++;
    });

    // Atualizar contador se fornecido
    if (counterId) {
      const counter = document.getElementById(counterId);
      if (counter) {
        counter.textContent = `Resultados encontrados: ${visibleCount}`;
      }
    }
  }
}

// =================================
// UTILITÁRIOS
// =================================

/**
 * Confirma uma ação antes de executar
 * @param {string} message - Mensagem de confirmação
 * @param {Function} callback - Função a ser executada se confirmado
 */
function confirmarAcao(message, callback) {
  if (typeof confirm !== 'undefined' && confirm(message)) {
    callback();
  }
}

/**
 * Mostra uma mensagem temporária
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo da mensagem (success, error, warning, info)
 * @param {number} duration - Duração em ms (padrão: 3000ms)
 */
function mostrarMensagem(message, type = 'info', duration = 3000) {
  if (typeof document !== 'undefined') {
    // Criar elemento da mensagem
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          padding: 12px 20px;
          border-radius: 8px;
          color: white;
          font-weight: 500;
          z-index: 9999;
          animation: slideInRight 0.3s ease;
      `;

    // Cores por tipo
    const allowedTypes = ['success', 'error', 'warning', 'info'];
    const colors = {
      success: '#28a745',
      error: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8'
    };
    const safeType = allowedTypes.includes(type) ? type : 'info';
    messageEl.style.backgroundColor = colors[safeType];

    // Adicionar ao DOM
    document.body.appendChild(messageEl);

    // Remover após o tempo especificado
    if (typeof setTimeout !== 'undefined') {
      setTimeout(() => {
        messageEl.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
          if (messageEl.parentNode) {
            messageEl.parentNode.removeChild(messageEl);
          }
        }, 300);
      }, duration);
    }
  }
}

/**
 * Adiciona CSS para animações das mensagens
 */
function addMessageAnimations() {
  if (typeof document !== 'undefined') {
    if (document.getElementById('message-animations')) return;

    const style = document.createElement('style');
    style.id = 'message-animations';
    style.textContent = `
      @keyframes slideInRight {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
          
      @keyframes slideOutRight {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

/**
 * Gerencia as mensagens Django que aparecem no template
 * Adiciona funcionalidades de auto-dismiss e fechamento manual
 */
function setupDjangoMessages() {
  if (typeof document !== 'undefined') {
    const messages = document.querySelectorAll('.messages li');

    if (messages.length === 0) return;

    messages.forEach((message, index) => {
      // Adiciona delay na animação para mensagens múltiplas
      message.style.animationDelay = `${index * 0.1}s`;

      // Auto-dismiss após 5 segundos (exceto para mensagens de erro)
      if (!message.classList.contains('error') && typeof setTimeout !== 'undefined') {
        setTimeout(() => {
          if (message.parentNode) {
            message.style.animation = 'message-dismiss 0.5s ease-in forwards';
            setTimeout(() => {
              if (message.parentNode) {
                message.remove();
              }
            }, 500);
          }
        }, 5000 + (index * 1000)); // Cada mensagem adiciona 1s ao delay
      }

      // Adiciona evento de clique para fechar mensagem
      message.addEventListener('click', function () {
        this.style.animation = 'message-dismiss 0.3s ease-in forwards';
        if (typeof setTimeout !== 'undefined') {
          setTimeout(() => {
            if (this.parentNode) {
              this.remove();
            }
          }, 300);
        } else {
          if (this.parentNode) {
            this.remove();
          }
        }
      });

      // Melhora a acessibilidade
      message.setAttribute('role', 'alert');
      message.setAttribute('tabindex', '0');
      message.title = 'Clique para fechar esta mensagem';

      // Suporte a teclado
      message.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.click();
        }
      });
    });

    if (typeof console !== 'undefined') {
      console.log(`✅ ${messages.length} mensagem(ns) Django configurada(s)`);
    }
  }
}

// =================================
// INICIALIZAÇÃO GLOBAL
// =================================

/**
 * Inicializa todas as funcionalidades globais
 */
function initGlobalFeatures() {
  // Habilitar drag scroll em tabelas
  enableDragScroll();

  // Configurar eventos de modais
  setupModalEvents();

  // Adicionar animações de mensagens
  addMessageAnimations();

  // Configurar mensagens Django
  setupDjangoMessages();

  if (typeof console !== 'undefined') {
    console.log('✅ Funcionalidades globais de gerenciamento inicializadas');
  }
}

// =================================
// AUTO-INICIALIZAÇÃO
// =================================

// Inicializar quando o DOM estiver carregado
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', initGlobalFeatures);

  // Também inicializar se o script for carregado após o DOM estar pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGlobalFeatures);
  } else {
    initGlobalFeatures();
  }
}

// =================================
// EXPORTAR PARA ESCOPO GLOBAL
// =================================

// Disponibilizar funções no escopo global para compatibilidade
if (typeof window !== 'undefined') {
  window.enableDragScroll = enableDragScroll;
  window.openModal = openModal;
  window.closeModal = closeModal;
  window.aplicarFiltros = aplicarFiltros;
  window.limparFiltros = limparFiltros;
  window.filterTable = filterTable;
  window.confirmarAcao = confirmarAcao;
  window.mostrarMensagem = mostrarMensagem;
  window.setupAutoSearch = setupAutoSearch;
  window.setupDjangoMessages = setupDjangoMessages;
}
