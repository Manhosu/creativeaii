-- Migração: Criar tabela de categorias ativas
-- Data: 2025-06-09
-- Descrição: Sistema de seleção de categorias para filtrar scraping, geração e publicação

CREATE TABLE IF NOT EXISTS active_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_key TEXT NOT NULL UNIQUE,
    category_name TEXT NOT NULL,
    category_url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    auto_detected BOOLEAN DEFAULT FALSE,
    products_count INTEGER DEFAULT 0,
    last_scraped TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_active_categories_active ON active_categories(is_active);
CREATE INDEX IF NOT EXISTS idx_active_categories_priority ON active_categories(priority DESC);
CREATE INDEX IF NOT EXISTS idx_active_categories_key ON active_categories(category_key);

-- Trigger para atualizar updated_at
CREATE TRIGGER IF NOT EXISTS update_active_categories_timestamp 
    AFTER UPDATE ON active_categories
    FOR EACH ROW
    BEGIN
        UPDATE active_categories 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;

-- Inserir categorias padrão conforme header do site
INSERT OR IGNORE INTO active_categories (category_key, category_name, category_url, is_active, priority, auto_detected) VALUES
('impressoras', 'IMPRESSORAS', 'https://www.creativecopias.com.br/impressoras', TRUE, 1, TRUE),
('cartuchos-de-toner', 'CARTUCHOS DE TONER', 'https://www.creativecopias.com.br/cartuchos-de-toner', TRUE, 2, TRUE),
('cartuchos-de-tinta', 'CARTUCHOS DE TINTA', 'https://www.creativecopias.com.br/cartuchos-de-tinta', TRUE, 3, TRUE),
('refil-de-toner', 'REFIL DE TONER', 'https://www.creativecopias.com.br/refil-de-toner', TRUE, 4, TRUE),
('refil-de-tinta', 'REFIL DE TINTA', 'https://www.creativecopias.com.br/refil-de-tinta', TRUE, 5, TRUE),
('pecas', 'PEÇAS', 'https://www.creativecopias.com.br/pecas', TRUE, 6, TRUE),
('demais-departamentos', 'DEMAIS DEPARTAMENTOS', 'https://www.creativecopias.com.br/departamentos', TRUE, 7, TRUE); 