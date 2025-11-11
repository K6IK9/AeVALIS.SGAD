/**
 * relatorio-avaliacoes.js
 * Funcionalidades para a tela de relatórios de avaliações
 */

/* eslint-env browser */
/* global window, document, console, URL, FormData, setTimeout, clearTimeout */

// ============= Função para Limpar Filtros =============
function limparFiltros() {
  // Redirecionar para a página sem parâmetros de query
  window.location.href = window.location.pathname;
}

// ============= Função para Exportar CSV =============
function exportarCSV() {
  const form = document.getElementById('form-filtros');

  if (!form) {
    console.error('Formulário de filtros não encontrado');
    return;
  }

  // Criar URL com os parâmetros atuais do formulário
  const url = new URL(window.location.href);

  // Adicionar todos os parâmetros do formulário à URL
  const formData = new FormData(form);
  for (let [key, value] of formData.entries()) {
    if (value && value.trim() !== '') {
      url.searchParams.set(key, value);
    }
  }

  // Adicionar parâmetro de formato CSV
  url.searchParams.set('formato', 'csv');

  // Redirecionar para download do CSV
  window.location.href = url.toString();
}

// ============= Função para Alterar Itens por Página =============
document.addEventListener('DOMContentLoaded', function () {
  const itemsPerPageSelect = document.getElementById('items-per-page');

  if (itemsPerPageSelect) {
    itemsPerPageSelect.addEventListener('change', function () {
      const form = document.getElementById('form-filtros');
      const url = new URL(window.location.href);

      // Preservar filtros existentes
      const formData = new FormData(form);
      for (let [key, value] of formData.entries()) {
        if (value && value.trim() !== '') {
          url.searchParams.set(key, value);
        }
      }

      // Atualizar per_page e resetar para página 1
      url.searchParams.set('per_page', this.value);
      url.searchParams.set('page', '1');

      // Redirecionar
      window.location.href = url.toString();
    });
  }

  // ============= Adicionar Overlay de Loading =============
  const loadingOverlay = document.getElementById('loading-overlay');

  // Mostrar loading ao submeter formulário ou exportar
  const formFiltros = document.getElementById('form-filtros');
  if (formFiltros) {
    formFiltros.addEventListener('submit', function () {
      if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
      }
    });
  }

  // ============= Busca em Tempo Real (opcional - debounced) =============
  const searchInput = document.getElementById('search-avaliacoes');
  let searchTimeout;

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimeout);

      // Aguardar 500ms após parar de digitar para submeter
      searchTimeout = setTimeout(function () {
        if (formFiltros && searchInput.value.length >= 3 || searchInput.value.length === 0) {
          // Submeter formulário automaticamente
          // Comentado por padrão - descomente se quiser busca automática
          // formFiltros.submit();
        }
      }, 500);
    });
  }

  // ============= Drag Scroll para Tabelas (se necessário) =============
  const scrollableElements = document.querySelectorAll('[data-drag-scroll]');

  scrollableElements.forEach(element => {
    let isDown = false;
    let startX;
    let scrollLeft;

    element.addEventListener('mousedown', (e) => {
      isDown = true;
      element.style.cursor = 'grabbing';
      startX = e.pageX - element.offsetLeft;
      scrollLeft = element.scrollLeft;
    });

    element.addEventListener('mouseleave', () => {
      isDown = false;
      element.style.cursor = 'grab';
    });

    element.addEventListener('mouseup', () => {
      isDown = false;
      element.style.cursor = 'grab';
    });

    element.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - element.offsetLeft;
      const walk = (x - startX) * 2;
      element.scrollLeft = scrollLeft - walk;
    });
  });
});
