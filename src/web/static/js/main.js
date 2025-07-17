// Sistema de Triagem Hospitalar - JavaScript principal
// Foco em acessibilidade e funcionalidade

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar sistema
    initializeSystem();
    
    // Configurar acessibilidade
    setupAccessibility();
    
    // Configurar validação de formulários
    setupFormValidation();
    
    // Configurar atalhos de teclado
    setupKeyboardShortcuts();
});

/**
 * Inicializar sistema
 */
function initializeSystem() {
    console.log('Sistema de Triagem Hospitalar Inteligente inicializado');
    
    // Verificar suporte a JavaScript
    document.body.classList.add('js-enabled');
    
    // Anunciar status para leitores de tela
    announceToScreenReader('Sistema de triagem carregado e pronto para uso');
}

/**
 * Configurar recursos de acessibilidade
 */
function setupAccessibility() {
    // Melhorar navegação por teclado
    enhanceKeyboardNavigation();
    
    // Configurar anúncios para leitores de tela
    setupScreenReaderAnnouncements();
    
    // Adicionar skip links dinâmicos
    addSkipLinks();
}

/**
 * Melhorar navegação por teclado
 */
function enhanceKeyboardNavigation() {
    // Adicionar indicadores visuais de foco
    const focusableElements = document.querySelectorAll(
        'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        element.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    });
    
    // Navegação com setas em grupos de radio buttons
    const radioGroups = document.querySelectorAll('input[type="radio"]');
    radioGroups.forEach(radio => {
        radio.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                e.preventDefault();
                navigateRadioGroup(this, 'next');
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                e.preventDefault();
                navigateRadioGroup(this, 'prev');
            }
        });
    });
}

/**
 * Navegar entre radio buttons
 */
function navigateRadioGroup(currentRadio, direction) {
    const radioGroup = document.querySelectorAll(`input[name="${currentRadio.name}"]`);
    const currentIndex = Array.from(radioGroup).indexOf(currentRadio);
    
    let nextIndex;
    if (direction === 'next') {
        nextIndex = (currentIndex + 1) % radioGroup.length;
    } else {
        nextIndex = (currentIndex - 1 + radioGroup.length) % radioGroup.length;
    }
    
    radioGroup[nextIndex].focus();
    radioGroup[nextIndex].checked = true;
}

/**
 * Configurar anúncios para leitores de tela
 */
function setupScreenReaderAnnouncements() {
    // Criar região para anúncios
    const announceRegion = document.createElement('div');
    announceRegion.id = 'announce-region';
    announceRegion.setAttribute('aria-live', 'polite');
    announceRegion.setAttribute('aria-atomic', 'true');
    announceRegion.className = 'sr-only';
    document.body.appendChild(announceRegion);
    
    // Anunciar mudanças de estado
    const form = document.querySelector('.triagem-form');
    if (form) {
        form.addEventListener('submit', function() {
            announceToScreenReader('Processando triagem, aguarde...');
        });
    }
}

/**
 * Anunciar mensagem para leitores de tela
 */
function announceToScreenReader(message) {
    const announceRegion = document.getElementById('announce-region');
    if (announceRegion) {
        announceRegion.textContent = message;
        
        // Limpar após 5 segundos
        setTimeout(() => {
            announceRegion.textContent = '';
        }, 5000);
    }
}

/**
 * Adicionar skip links dinâmicos
 */
function addSkipLinks() {
    const mainContent = document.getElementById('main-content');
    const form = document.querySelector('.triagem-form');
    
    if (form && mainContent) {
        const skipToForm = document.createElement('a');
        skipToForm.href = '#triagem-form';
        skipToForm.className = 'skip-link';
        skipToForm.textContent = 'Ir para o formulário de triagem';
        
        mainContent.insertBefore(skipToForm, mainContent.firstChild);
        
        // Adicionar ID ao formulário
        form.id = 'triagem-form';
    }
}

/**
 * Configurar validação de formulários
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                announceToScreenReader('Formulário contém erros. Verifique os campos destacados.');
            }
        });
        
        // Validação em tempo real
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

/**
 * Validar formulário completo
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Validar campo individual
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Verificar se é obrigatório
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo é obrigatório';
    }
    
    // Validações específicas por tipo
    if (value && field.type === 'number') {
        const num = parseFloat(value);
        const min = parseFloat(field.min);
        const max = parseFloat(field.max);
        
        if (isNaN(num)) {
            isValid = false;
            errorMessage = 'Digite um número válido';
        } else if (min !== null && num < min) {
            isValid = false;
            errorMessage = `Valor deve ser no mínimo ${min}`;
        } else if (max !== null && num > max) {
            isValid = false;
            errorMessage = `Valor deve ser no máximo ${max}`;
        }
    }
    
    // Validação específica para pressão arterial
    if (field.name === 'pressao_diastolica') {
        const sistolica = document.querySelector('input[name="pressao_sistolica"]');
        if (sistolica && parseFloat(value) >= parseFloat(sistolica.value)) {
            isValid = false;
            errorMessage = 'Pressão diastólica deve ser menor que sistólica';
        }
    }
    
    // Exibir ou limpar erro
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

/**
 * Mostrar erro no campo
 */
function showFieldError(field, message) {
    // Remover erro anterior
    clearFieldError(field);
    
    // Adicionar classes de erro
    field.classList.add('error');
    field.setAttribute('aria-invalid', 'true');
    
    // Criar elemento de erro
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.id = `${field.id}-error`;
    errorElement.textContent = message;
    errorElement.setAttribute('role', 'alert');
    
    // Inserir após o campo
    field.parentNode.insertBefore(errorElement, field.nextSibling);
    
    // Conectar com aria-describedby
    const describedBy = field.getAttribute('aria-describedby') || '';
    field.setAttribute('aria-describedby', `${describedBy} ${errorElement.id}`.trim());
}

/**
 * Limpar erro do campo
 */
function clearFieldError(field) {
    field.classList.remove('error');
    field.setAttribute('aria-invalid', 'false');
    
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
    
    // Limpar aria-describedby
    const describedBy = field.getAttribute('aria-describedby');
    if (describedBy) {
        const errorId = `${field.id}-error`;
        const newDescribedBy = describedBy.replace(errorId, '').trim();
        if (newDescribedBy) {
            field.setAttribute('aria-describedby', newDescribedBy);
        } else {
            field.removeAttribute('aria-describedby');
        }
    }
}

/**
 * Configurar atalhos de teclado
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Alt + T: Ir para triagem
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            const triagemLink = document.querySelector('a[href*="triagem"]');
            if (triagemLink) {
                triagemLink.click();
            }
        }
        
        // Alt + H: Ir para home
        if (e.altKey && e.key === 'h') {
            e.preventDefault();
            const homeLink = document.querySelector('a[href*="index"]') || 
                           document.querySelector('a[href="/"]');
            if (homeLink) {
                homeLink.click();
            }
        }
        
        // Escape: Fechar modais ou resetar formulário
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal);
            } else {
                const form = document.querySelector('form');
                if (form && confirm('Deseja limpar o formulário?')) {
                    form.reset();
                    announceToScreenReader('Formulário limpo');
                }
            }
        }
    });
}

/**
 * Utilitários para modal (se necessário)
 */
function closeModal(modal) {
    modal.classList.remove('active');
    
    // Restaurar foco
    const trigger = modal.dataset.trigger;
    if (trigger) {
        const triggerElement = document.querySelector(trigger);
        if (triggerElement) {
            triggerElement.focus();
        }
    }
}

/**
 * Função para preencher dados de exemplo
 */
async function preencherExemplo() {
    try {
        announceToScreenReader('Carregando dados de exemplo...');
        
        const response = await fetch('/paciente-exemplo');
        if (!response.ok) {
            throw new Error('Erro ao carregar dados');
        }
        
        const data = await response.json();
        
        // Preencher campos
        fillFormWithData(data);
        
        announceToScreenReader('Dados de exemplo carregados com sucesso');
        
    } catch (error) {
        console.error('Erro ao carregar exemplo:', error);
        announceToScreenReader('Erro ao carregar dados de exemplo');
        alert('Erro ao carregar dados de exemplo. Tente novamente.');
    }
}

/**
 * Preencher formulário com dados
 */
function fillFormWithData(data) {
    // Campos numéricos
    const numericFields = [
        'idade', 'pressao_sistolica', 'pressao_diastolica',
        'frequencia_cardiaca', 'saturacao_oxigenio', 'temperatura'
    ];
    
    numericFields.forEach(field => {
        const input = document.getElementById(field);
        if (input && data[field] !== undefined) {
            input.value = data[field];
        }
    });
    
    // Sexo
    if (data.sexo) {
        const sexoRadio = document.getElementById(`sexo-${data.sexo.toLowerCase()}`);
        if (sexoRadio) {
            sexoRadio.checked = true;
        }
    }
    
    // Sintomas (checkboxes)
    const symptoms = [
        'dor_peito', 'dificuldade_respiratoria', 'febre',
        'tontura', 'vomito', 'dor_abdominal'
    ];
    
    symptoms.forEach(symptom => {
        const checkbox = document.getElementById(symptom);
        if (checkbox && data[symptom] !== undefined) {
            checkbox.checked = data[symptom];
        }
    });
}

/**
 * Função para salvar resultado
 */
function salvarResultado() {
    try {
        const resultadoElement = document.querySelector('.resultado-card');
        if (!resultadoElement) {
            throw new Error('Resultado não encontrado');
        }
        
        // Coletar dados do resultado
        const classificacao = document.querySelector('.risco-info h3')?.textContent || '';
        const confianca = document.querySelector('.confianca')?.textContent || '';
        const raciocinio = document.querySelector('.raciocinio-texto')?.textContent || '';
        
        const recomendacoes = Array.from(document.querySelectorAll('.recomendacoes-lista li'))
            .map(li => li.textContent);
        
        const resultado = {
            classificacao,
            confianca,
            raciocinio,
            recomendacoes,
            timestamp: new Date().toISOString()
        };
        
        // Criar arquivo para download
        const blob = new Blob([JSON.stringify(resultado, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `triagem_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        announceToScreenReader('Resultado salvo com sucesso');
        
    } catch (error) {
        console.error('Erro ao salvar resultado:', error);
        announceToScreenReader('Erro ao salvar resultado');
        alert('Erro ao salvar resultado. Tente novamente.');
    }
}

/**
 * Função para imprimir resultado
 */
function imprimirResultado() {
    announceToScreenReader('Preparando impressão...');
    
    // Adicionar estilos específicos para impressão
    const printStyles = `
        <style>
            @media print {
                .resultado-acoes, header, footer { display: none !important; }
                .resultado-card { 
                    box-shadow: none !important; 
                    border: 2px solid #000 !important;
                }
                .risco-badge { 
                    -webkit-print-color-adjust: exact !important;
                    color-adjust: exact !important;
                }
            }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', printStyles);
    
    // Imprimir
    window.print();
    
    announceToScreenReader('Documento enviado para impressão');
}

/**
 * Configurar tema (claro/escuro)
 */
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'light' 
            ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        announceToScreenReader(`Tema alterado para ${newTheme === 'light' ? 'claro' : 'escuro'}`);
    });
}

/**
 * Configurar fonte (tamanho)
 */
function setupFontSizeToggle() {
    const fontSizeButtons = document.querySelectorAll('[data-font-size]');
    
    fontSizeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const size = this.dataset.fontSize;
            document.documentElement.style.fontSize = size;
            localStorage.setItem('fontSize', size);
            
            announceToScreenReader(`Tamanho da fonte alterado para ${size}`);
        });
    });
    
    // Aplicar tamanho salvo
    const savedSize = localStorage.getItem('fontSize');
    if (savedSize) {
        document.documentElement.style.fontSize = savedSize;
    }
}

// Exportar funções globais
window.preencherExemplo = preencherExemplo;
window.salvarResultado = salvarResultado;
window.imprimirResultado = imprimirResultado;
