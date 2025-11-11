/**
 * form-validation.js
 * Biblioteca de validação de formulários reutilizável
 * Sistema de Avaliação Docente SUAP
 */

// =================================
// VALIDADORES
// =================================

/**
 * Validador para campos de matrícula (apenas números)
 * @param {string} value - Valor a ser validado
 * @param {boolean} isRequired - Se o campo é obrigatório
 * @param {number} maxLength - Comprimento máximo
 * @returns {Object} {valid: boolean, errors: string[]}
 */
function validateMatricula(value, isRequired = true, maxLength = 20) {
  const errors = [];
  const trimmedValue = value.trim();

  if (isRequired && trimmedValue.length === 0) {
    errors.push('Este campo é obrigatório.');
  } else if (trimmedValue.length > 0) {
    if (!/^\d+$/.test(trimmedValue)) {
      errors.push('Deve conter apenas números.');
    }
    if (trimmedValue.length > maxLength) {
      errors.push(`Deve ter no máximo ${maxLength} dígitos.`);
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors
  };
}

/**
 * Validador para senhas
 * @param {string} password - Senha a ser validada
 * @returns {Object} {valid: boolean, errors: string[]}
 */
function validatePassword(password) {
  const errors = [];

  // Só valida se algo foi digitado
  if (password.length > 0) {
    if (password.length < 8) {
      errors.push('A senha deve ter pelo menos 8 caracteres.');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('A senha deve conter pelo menos uma letra minúscula.');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('A senha deve conter pelo menos uma letra maiúscula.');
    }
    if (!/\d/.test(password)) {
      errors.push('A senha deve conter pelo menos um número.');
    }

    // Verifica senhas comuns
    const commonPasswords = [
      '12345678', 'password', '123456789', 'qwerty',
      'abc123', 'password1', '11111111', '00000000'
    ];
    if (commonPasswords.includes(password.toLowerCase())) {
      errors.push('Esta senha é muito comum. Escolha uma senha mais segura.');
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors
  };
}

/**
 * Validador para email
 * @param {string} email - Email a ser validado
 * @param {boolean} isRequired - Se o campo é obrigatório
 * @returns {Object} {valid: boolean, errors: string[]}
 */
function validateEmail(email, isRequired = true) {
  const errors = [];
  const trimmedEmail = email.trim();

  if (isRequired && trimmedEmail.length === 0) {
    errors.push('O email é obrigatório.');
  } else if (trimmedEmail.length > 0) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(trimmedEmail)) {
      errors.push('Digite um email válido.');
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors
  };
}

/**
 * Validador para nomes (apenas letras e espaços)
 * @param {string} name - Nome a ser validado
 * @param {boolean} isRequired - Se o campo é obrigatório
 * @param {number} minLength - Comprimento mínimo
 * @returns {Object} {valid: boolean, errors: string[]}
 */
function validateName(name, isRequired = true, minLength = 2) {
  const errors = [];
  const trimmedName = name.trim();

  if (isRequired && trimmedName.length === 0) {
    errors.push('Este campo é obrigatório.');
  } else if (trimmedName.length > 0) {
    if (trimmedName.length < minLength) {
      errors.push(`Deve ter pelo menos ${minLength} caracteres.`);
    }
    if (!/^[a-zA-ZÀ-ÿ\s]+$/.test(trimmedName)) {
      errors.push('Deve conter apenas letras.');
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors
  };
}

// =================================
// GERENCIAMENTO DE ERROS
// =================================

/**
 * Mostra mensagens de erro em um campo
 * @param {HTMLElement} input - Elemento de input
 * @param {string[]} errors - Array de mensagens de erro
 */
function showFieldErrors(input, errors) {
  if (!input) return;

  // Limpa erros existentes primeiro
  clearFieldErrors(input);

  if (errors.length > 0) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.innerHTML = errors.join('<br>');
    errorDiv.setAttribute('role', 'alert');

    const container = getFieldContainer(input);
    if (container) {
      container.appendChild(errorDiv);
    }

    input.classList.add('error');
    input.setAttribute('aria-invalid', 'true');
  }
}

/**
 * Limpa mensagens de erro de um campo
 * @param {HTMLElement} input - Elemento de input
 */
function clearFieldErrors(input) {
  if (!input) return;

  const container = getFieldContainer(input);
  if (container) {
    const existingError = container.querySelector('.field-error');
    if (existingError) {
      existingError.remove();
    }
  }

  input.classList.remove('error');
  input.removeAttribute('aria-invalid');
}

/**
 * Obtém o container do campo
 * @param {HTMLElement} input - Elemento de input
 * @returns {HTMLElement|null} Container do campo
 */
function getFieldContainer(input) {
  if (!input) return null;
  return input.closest('.form-group') || input.parentElement;
}

// =================================
// CONFIGURADORES DE VALIDAÇÃO
// =================================

/**
 * Configura validação automática para campo de matrícula
 * @param {string} inputId - ID do campo de input
 * @param {string} fieldLabel - Label do campo para mensagens
 * @param {boolean} isRequired - Se o campo é obrigatório
 * @param {Function} validatorFn - Função validadora customizada (opcional)
 */
function setupMatriculaValidation(inputId, fieldLabel = 'Matrícula', isRequired = true, validatorFn = null) {
  const input = document.getElementById(inputId);
  if (!input) return;

  // Sanitização em tempo real - remove não-numéricos
  input.addEventListener('input', function () {
    this.value = this.value.replace(/\D/g, '');
    clearFieldErrors(this);
  });

  // Validação ao sair do campo
  input.addEventListener('blur', function () {
    const value = this.value.trim();

    // Se campo não obrigatório e vazio, não validar
    if (!isRequired && value.length === 0) {
      clearFieldErrors(this);
      return;
    }

    // Usa validador customizado ou padrão
    const result = validatorFn ? validatorFn(value) : validateMatricula(value, isRequired);

    if (!result.valid) {
      const errors = result.errors.map(err => `${fieldLabel}: ${err}`);
      showFieldErrors(this, errors);
    } else {
      clearFieldErrors(this);
    }
  });
}

/**
 * Configura validação automática para campo de senha
 * @param {string} inputId - ID do campo de input
 * @param {Function} validatorFn - Função validadora customizada (opcional)
 */
function setupPasswordValidation(inputId, validatorFn = null) {
  const input = document.getElementById(inputId);
  if (!input) return;

  // Limpa erros ao digitar
  input.addEventListener('input', function () {
    clearFieldErrors(this);
  });

  // Validação ao sair do campo
  input.addEventListener('blur', function () {
    const password = this.value;

    // Só valida se algo foi digitado
    if (password.length === 0) {
      clearFieldErrors(this);
      return;
    }

    const result = validatorFn ? validatorFn(password) : validatePassword(password);

    if (!result.valid) {
      showFieldErrors(this, result.errors);
    } else {
      clearFieldErrors(this);
    }
  });
}

/**
 * Configura validação automática para campo de email
 * @param {string} inputId - ID do campo de input
 * @param {boolean} isRequired - Se o campo é obrigatório
 */
function setupEmailValidation(inputId, isRequired = true) {
  const input = document.getElementById(inputId);
  if (!input) return;

  input.addEventListener('input', function () {
    clearFieldErrors(this);
  });

  input.addEventListener('blur', function () {
    const result = validateEmail(this.value, isRequired);

    if (!result.valid) {
      showFieldErrors(this, result.errors);
    } else {
      clearFieldErrors(this);
    }
  });
}

/**
 * Configura validação automática para campo de nome
 * @param {string} inputId - ID do campo de input
 * @param {string} fieldLabel - Label do campo
 * @param {boolean} isRequired - Se o campo é obrigatório
 */
function setupNameValidation(inputId, fieldLabel = 'Nome', isRequired = true) {
  const input = document.getElementById(inputId);
  if (!input) return;

  input.addEventListener('input', function () {
    clearFieldErrors(this);
  });

  input.addEventListener('blur', function () {
    const result = validateName(this.value, isRequired);

    if (!result.valid) {
      const errors = result.errors.map(err => `${fieldLabel}: ${err}`);
      showFieldErrors(this, errors);
    } else {
      clearFieldErrors(this);
    }
  });
}

// =================================
// VALIDAÇÃO DE FORMULÁRIO COMPLETO
// =================================

/**
 * Valida todos os campos de um formulário
 * @param {Object} fieldValidations - Objeto com validações {inputId: validatorFunction}
 * @returns {boolean} true se todos os campos são válidos
 */
function validateForm(fieldValidations) {
  let hasErrors = false;
  let firstErrorField = null;

  Object.entries(fieldValidations).forEach(([inputId, validator]) => {
    const input = document.getElementById(inputId);
    if (!input) return;

    const result = validator(input.value);

    if (!result.valid) {
      showFieldErrors(input, result.errors);
      hasErrors = true;
      if (!firstErrorField) {
        firstErrorField = input;
      }
    } else {
      clearFieldErrors(input);
    }
  });

  // Foca no primeiro campo com erro
  if (firstErrorField) {
    firstErrorField.focus();
    firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  return !hasErrors;
}

/**
 * Mostra mensagem de erro no topo do formulário
 * @param {string} message - Mensagem a ser exibida
 * @param {string} formSelector - Seletor CSS do formulário
 */
function showFormErrorMessage(message, formSelector = 'form') {
  const form = document.querySelector(formSelector);
  if (!form) return;

  // Remove mensagens existentes
  const existingMessages = form.querySelector('.messages');
  if (existingMessages) {
    existingMessages.remove();
  }

  // Cria nova mensagem
  const messagesContainer = document.createElement('ul');
  messagesContainer.className = 'messages';

  const messageItem = document.createElement('li');
  messageItem.className = 'error';
  messageItem.textContent = message;

  messagesContainer.appendChild(messageItem);

  // Insere no início do formulário
  form.insertBefore(messagesContainer, form.firstChild);
}

// =================================
// EXPORTAR PARA ESCOPO GLOBAL
// =================================

if (typeof window !== 'undefined') {
  // Validadores
  window.validateMatricula = validateMatricula;
  window.validatePassword = validatePassword;
  window.validateEmail = validateEmail;
  window.validateName = validateName;

  // Gerenciamento de erros
  window.showFieldErrors = showFieldErrors;
  window.clearFieldErrors = clearFieldErrors;
  window.getFieldContainer = getFieldContainer;

  // Configuradores
  window.setupMatriculaValidation = setupMatriculaValidation;
  window.setupPasswordValidation = setupPasswordValidation;
  window.setupEmailValidation = setupEmailValidation;
  window.setupNameValidation = setupNameValidation;

  // Validação de formulário
  window.validateForm = validateForm;
  window.showFormErrorMessage = showFormErrorMessage;
}
