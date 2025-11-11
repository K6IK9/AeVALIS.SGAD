document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.getElementById('toggleLoginMode');
  const backButton = document.getElementById('backToSuap');
  const suapMode = document.getElementById('suapMode');
  const traditionalMode = document.getElementById('traditionalMode');
  const loginForm = document.getElementById('loginForm');

  // Função para alternar para modo tradicional
  function showTraditionalMode() {
    suapMode.classList.remove('active');
    traditionalMode.classList.add('active');
    // Focar no campo de username
    setTimeout(() => {
      document.getElementById('id_username').focus();
    }, 300);
  }

  // Função para voltar ao modo SUAP
  function showSuapMode() {
    traditionalMode.classList.remove('active');
    suapMode.classList.add('active');
  }

  // Event listeners para os botões de toggle
  if (toggleButton) {
    toggleButton.addEventListener('click', function (e) {
      e.preventDefault();
      showTraditionalMode();
    });
  }

  if (backButton) {
    backButton.addEventListener('click', function (e) {
      e.preventDefault();
      showSuapMode();
    });
  }

  // Toggle de visibilidade da senha
  const togglePasswordButtons = document.querySelectorAll('.toggle-password');
  togglePasswordButtons.forEach(button => {
    button.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const targetInput = document.getElementById(targetId);

      if (targetInput.type === 'password') {
        targetInput.type = 'text';
        this.innerHTML = '<img src="{% static \'assets/eye-off.svg\' %}" alt="Ocultar senha">';
      } else {
        targetInput.type = 'password';
        this.innerHTML = '<img src="{% static \'assets/eye.svg\' %}" alt="Mostrar senha">';
      }
    });
  });

  // Validação básica do formulário tradicional
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      if (traditionalMode.classList.contains('active')) {
        const username = document.getElementById('id_username').value.trim();
        const password = document.getElementById('id_password').value.trim();

        if (!username || !password) {
          e.preventDefault();
          alert('Por favor, preencha todos os campos.');
          return false;
        }
      }
    });
  }

  // Animações de entrada
  setTimeout(() => {
    document.body.classList.add('loaded');
  }, 100);
});