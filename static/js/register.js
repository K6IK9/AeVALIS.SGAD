/**
 * REGISTER PAGE SCRIPTS - Sistema de Avaliação Docente
 * Funcionalidades específicas da página de registro
 */

document.addEventListener('DOMContentLoaded', function () {
  // Funcionalidade de mostrar/ocultar senha
  initializePasswordToggles();

  // Validação em tempo real dos campos
  initializeFormValidation();

  // Animações de entrada
  initializeAnimations();
});

/**
 * Inicializa os toggles de visibilidade da senha
 */
function initializePasswordToggles() {
  const toggleButtons = document.querySelectorAll('.toggle-password');

  toggleButtons.forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();

      const targetId = this.getAttribute('data-target');
      const targetInput = document.getElementById(targetId);

      if (targetInput) {
        const isPassword = targetInput.type === 'password';
        targetInput.type = isPassword ? 'text' : 'password';

        // Atualiza o ícone (opcional - pode ser feito com CSS)
        const img = this.querySelector('img');
        if (img) {
          const iconName = isPassword ? 'eye-slash.svg' : 'eye.svg';
          img.src = img.src.replace(isPassword ? 'eye.svg' : 'eye-slash.svg', iconName);
          img.alt = isPassword ? 'Ocultar senha' : 'Mostrar senha';
        }

        // Feedback visual
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
          this.style.transform = 'scale(1)';
        }, 150);
      }
    });
  });
}

/**
 * Inicializa validação em tempo real dos campos do formulário
 */
function initializeFormValidation() {
  const form = document.getElementById('registerForm');
  if (!form) return;

  const fields = {
    'id_username': {
      minLength: 3,
      pattern: /^[a-zA-Z0-9_]+$/,
      message: 'A matrícula deve ter pelo menos 3 caracteres e conter apenas letras, números e underscore.'
    },
    'id_email': {
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: 'Digite um email válido.'
    },
    'id_first_name': {
      minLength: 2,
      pattern: /^[a-zA-ZÀ-ÿ\s]+$/,
      message: 'O nome deve ter pelo menos 2 caracteres e conter apenas letras.'
    },
    'id_last_name': {
      minLength: 2,
      pattern: /^[a-zA-ZÀ-ÿ\s]+$/,
      message: 'O sobrenome deve ter pelo menos 2 caracteres e conter apenas letras.'
    },
    'id_password1': {
      minLength: 8,
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      message: 'A senha deve ter pelo menos 8 caracteres, incluindo maiúscula, minúscula e número.'
    }
  };

  // Validação em tempo real
  Object.keys(fields).forEach(fieldId => {
    const input = document.getElementById(fieldId);
    if (input) {
      input.addEventListener('blur', function () {
        validateField(this, fields[fieldId]);
      });

      input.addEventListener('input', function () {
        clearFieldError(this);
      });
    }
  });

  // Validação de confirmação de senha
  const password2 = document.getElementById('id_password2');
  if (password2) {
    password2.addEventListener('blur', function () {
      validatePasswordConfirmation();
    });

    password2.addEventListener('input', function () {
      clearFieldError(this);
    });
  }

  // Validação no submit
  form.addEventListener('submit', function (e) {
    let isValid = true;

    // Valida todos os campos
    Object.keys(fields).forEach(fieldId => {
      const input = document.getElementById(fieldId);
      if (input && !validateField(input, fields[fieldId])) {
        isValid = false;
      }
    });

    // Valida confirmação de senha
    if (!validatePasswordConfirmation()) {
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault();
      showFormMessage('Por favor, corrija os erros destacados antes de continuar.', 'error');
    }
  });
}

/**
 * Valida um campo específico
 */
function validateField(input, rules) {
  const value = input.value.trim();
  let isValid = true;
  let message = '';

  // Verifica se está vazio (para campos obrigatórios)
  if (!value && input.hasAttribute('required')) {
    isValid = false;
    message = 'Este campo é obrigatório.';
  }
  // Verifica comprimento mínimo
  else if (rules.minLength && value.length < rules.minLength) {
    isValid = false;
    message = rules.message;
  }
  // Verifica padrão
  else if (rules.pattern && !rules.pattern.test(value)) {
    isValid = false;
    message = rules.message;
  }

  if (!isValid) {
    showFieldError(input, message);
  } else {
    clearFieldError(input);
  }

  return isValid;
}

/**
 * Valida confirmação de senha
 */
function validatePasswordConfirmation() {
  const password1 = document.getElementById('id_password1');
  const password2 = document.getElementById('id_password2');

  if (!password1 || !password2) return true;

  const pass1 = password1.value;
  const pass2 = password2.value;

  if (pass1 && pass2 && pass1 !== pass2) {
    showFieldError(password2, 'As senhas não coincidem.');
    return false;
  }

  clearFieldError(password2);
  return true;
}

/**
 * Mostra erro em um campo
 */
function showFieldError(input, message) {
  clearFieldError(input);

  const errorDiv = document.createElement('div');
  errorDiv.className = 'field-error';
  errorDiv.textContent = message;

  input.parentNode.appendChild(errorDiv);
  input.classList.add('error');
}

/**
 * Limpa erro de um campo
 */
function clearFieldError(input) {
  const existingError = input.parentNode.querySelector('.field-error');
  if (existingError) {
    existingError.remove();
  }
  input.classList.remove('error');
}

/**
 * Mostra mensagem no formulário
 */
function showFormMessage(message, type = 'info') {
  // Remove mensagens existentes
  const existingMessages = document.querySelector('.messages');
  if (existingMessages) {
    existingMessages.remove();
  }

  // Cria nova mensagem
  const messagesContainer = document.createElement('ul');
  messagesContainer.className = 'messages';

  const messageItem = document.createElement('li');
  messageItem.className = type;
  messageItem.textContent = message;

  messagesContainer.appendChild(messageItem);

  // Insere no início do formulário
  const form = document.getElementById('registerForm');
  if (form) {
    form.insertBefore(messagesContainer, form.firstChild);
  }
}

/**
 * Inicializa animações de entrada
 */
function initializeAnimations() {
  // Animação dos cards de informação
  const infoCards = document.querySelectorAll('.info-card');
  infoCards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';

    setTimeout(() => {
      card.style.transition = 'all 0.5s ease-out';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 * index);
  });
}

/**
 * Utilitários
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}