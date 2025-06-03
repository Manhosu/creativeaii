// Creative API - Sistema de Geração SEO - JavaScript Principal

// Utilitários
const API = {
    async get(url) {
        const response = await fetch(url);
        return response.json();
    },
    
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        return response.json();
    }
};

// Notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Loading spinner
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading';
    element.appendChild(spinner);
    return spinner;
}

function hideLoading(spinner) {
    if (spinner && spinner.parentNode) {
        spinner.parentNode.removeChild(spinner);
    }
}

// Atualizar status de módulos
async function updateModuleStatus() {
    const modules = ['scraper', 'generator', 'review', 'publisher', 'scheduler'];
    
    for (const module of modules) {
        try {
            const statusElement = document.getElementById(`${module}-status`);
            if (statusElement) {
                const response = await API.get(`/${module}`);
                statusElement.textContent = response.status || 'Ativo';
                statusElement.className = `status-badge ${response.status === 'Ativo' ? 'status-aprovado' : 'status-pendente'}`;
            }
        } catch (error) {
            console.error(`Erro ao verificar status do ${module}:`, error);
        }
    }
}

// Executar fluxo completo
async function runCompleteWorkflow() {
    const button = document.getElementById('run-workflow');
    const originalText = button.textContent;
    
    button.disabled = true;
    button.innerHTML = '<div class="loading"></div> Executando...';
    
    try {
        showNotification('Iniciando fluxo completo...', 'info');
        
        // 1. Scraping
        showNotification('Executando scraping...', 'info');
        await API.post('/scraper/run');
        
        // 2. Geração
        showNotification('Gerando artigos...', 'info');
        await API.post('/generator/generate');
        
        // 3. Atualizar lista de revisão
        showNotification('Fluxo concluído! Verifique os artigos para revisão.', 'success');
        
        // Recarregar página de revisão se estiver nela
        if (window.location.pathname.includes('/review')) {
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
        
    } catch (error) {
        console.error('Erro no fluxo:', error);
        showNotification('Erro durante execução do fluxo', 'error');
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
}

// Carregar artigos de revisão
async function loadReviewArticles(status = null) {
    const container = document.getElementById('articles-container');
    if (!container) return;
    
    const spinner = showLoading(container);
    
    try {
        const url = status ? `/review/articles?status=${status}` : '/review/articles';
        const response = await API.get(url);
        
        hideLoading(spinner);
        
        if (response.articles && response.articles.length > 0) {
            container.innerHTML = response.articles.map(article => `
                <div class="card article-card">
                    <h3>${article.titulo}</h3>
                    <p class="text-secondary">${article.meta_descricao}</p>
                    <div class="article-meta">
                        <span class="status-badge status-${article.status}">${article.status}</span>
                        <span class="text-small">Criado: ${new Date(article.data_criacao).toLocaleDateString()}</span>
                    </div>
                    <div class="article-actions">
                        <a href="/review/${article.id}/edit" class="btn btn-primary">✏️ Editar</a>
                        <button onclick="approveArticle(${article.id})" class="btn btn-success">✅ Aprovar</button>
                        <button onclick="rejectArticle(${article.id})" class="btn btn-danger">❌ Rejeitar</button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="card"><p>Nenhum artigo encontrado para revisão.</p></div>';
        }
    } catch (error) {
        hideLoading(spinner);
        console.error('Erro ao carregar artigos:', error);
        container.innerHTML = '<div class="card"><p class="text-danger">Erro ao carregar artigos.</p></div>';
    }
}

// Aprovar artigo
async function approveArticle(articleId) {
    try {
        await API.post(`/review/${articleId}/approve`, {
            comment: 'Aprovado automaticamente',
            reviewer: 'Sistema'
        });
        showNotification('Artigo aprovado com sucesso!', 'success');
        loadReviewArticles();
    } catch (error) {
        console.error('Erro ao aprovar artigo:', error);
        showNotification('Erro ao aprovar artigo', 'error');
    }
}

// Rejeitar artigo
async function rejectArticle(articleId) {
    const reason = prompt('Motivo da rejeição:');
    if (!reason) return;
    
    try {
        await API.post(`/review/${articleId}/reject`, {
            comment: reason,
            reviewer: 'Sistema'
        });
        showNotification('Artigo rejeitado!', 'info');
        loadReviewArticles();
    } catch (error) {
        console.error('Erro ao rejeitar artigo:', error);
        showNotification('Erro ao rejeitar artigo', 'error');
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Atualizar status dos módulos
    updateModuleStatus();
    
    // Carregar artigos se estiver na página de revisão
    if (window.location.pathname.includes('/review')) {
        loadReviewArticles();
    }
    
    // Atualizar status a cada 30 segundos
    setInterval(updateModuleStatus, 30000);
});

// Exportar funções globais
window.runCompleteWorkflow = runCompleteWorkflow;
window.loadReviewArticles = loadReviewArticles;
window.approveArticle = approveArticle;
window.rejectArticle = rejectArticle; 