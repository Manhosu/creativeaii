-- Script SQL para corrigir links quebrados no WordPress
-- ATENÇÃO: Faça backup do banco antes de executar!

-- CORREÇÃO URGENTE: Fix para links quebrados no WordPress
-- Execute este script no banco de dados WordPress para corrigir links quebrados

-- 1. Corrigir links de "Comprar" que apontam para URLs genéricas 
UPDATE wp_posts 
SET post_content = REPLACE(
    post_content, 
    'href="https://www.creativecopias.com.br">',
    'href="https://www.creativecopias.com.br/impressoras">'
) 
WHERE post_content LIKE '%Comprar%Impressora%' 
AND post_content LIKE '%href="https://www.creativecopias.com.br">%'
AND post_status = 'publish';

-- 2. Corrigir links para impressoras que apontam para URL genérica
UPDATE wp_posts 
SET post_content = REPLACE(
    post_content, 
    'href="https://www.creativecopias.com.br"',
    'href="https://www.creativecopias.com.br/impressoras"'
) 
WHERE post_content LIKE '%Comprar%' 
AND (post_content LIKE '%impressora%' OR post_content LIKE '%Impressora%')
AND post_content LIKE '%href="https://www.creativecopias.com.br"%'
AND post_status = 'publish';

-- 3. Corrigir links para cartuchos
UPDATE wp_posts 
SET post_content = REPLACE(
    post_content, 
    'href="https://www.creativecopias.com.br"',
    'href="https://www.creativecopias.com.br/cartuchos-de-tinta"'
) 
WHERE post_content LIKE '%Comprar%' 
AND (post_content LIKE '%cartucho%' OR post_content LIKE '%Cartucho%' OR post_content LIKE '%tinta%')
AND post_content LIKE '%href="https://www.creativecopias.com.br"%'
AND post_status = 'publish';

-- 4. Corrigir links para toners
UPDATE wp_posts 
SET post_content = REPLACE(
    post_content, 
    'href="https://www.creativecopias.com.br"',
    'href="https://www.creativecopias.com.br/cartuchos-de-toner"'
) 
WHERE post_content LIKE '%Comprar%' 
AND (post_content LIKE '%toner%' OR post_content LIKE '%Toner%')
AND post_content LIKE '%href="https://www.creativecopias.com.br"%'
AND post_status = 'publish';

-- 5. Corrigir links para scanners
UPDATE wp_posts 
SET post_content = REPLACE(
    post_content, 
    'href="https://www.creativecopias.com.br"',
    'href="https://www.creativecopias.com.br/scanner"'
) 
WHERE post_content LIKE '%Comprar%' 
AND (post_content LIKE '%scanner%' OR post_content LIKE '%Scanner%')
AND post_content LIKE '%href="https://www.creativecopias.com.br"%'
AND post_status = 'publish';

-- 6. Corrigir links para papel fotográfico
UPDATE wp_posts 
SET post_content = REPLACE(
    post_content, 
    'href="https://www.creativecopias.com.br"',
    'href="https://www.creativecopias.com.br/papel-fotografico"'
) 
WHERE post_content LIKE '%Comprar%' 
AND (post_content LIKE '%papel%' OR post_content LIKE '%Papel%')
AND post_content LIKE '%href="https://www.creativecopias.com.br"%'
AND post_status = 'publish';

-- 7. Mudança de texto de "Comprar" para "Consultar" (mais apropriado)
UPDATE wp_posts 
SET post_content = REPLACE(
    post_content, 
    '<strong>Comprar ',
    '<strong>Consultar '
) 
WHERE post_content LIKE '%<strong>Comprar %'
AND post_status = 'publish';

-- 8. Atualizar datas de modificação dos posts alterados
UPDATE wp_posts 
SET post_modified = NOW(), 
    post_modified_gmt = UTC_TIMESTAMP() 
WHERE post_content LIKE '%creativecopias.com.br%' 
AND post_status = 'publish'
AND post_modified < DATE_SUB(NOW(), INTERVAL 1 HOUR);

-- Verificação: Contar posts que ainda podem ter links problemáticos
SELECT 
    COUNT(*) as total_posts_com_links,
    SUM(CASE WHEN post_content LIKE '%href="https://www.creativecopias.com.br">%' THEN 1 ELSE 0 END) as links_genericos,
    SUM(CASE WHEN post_content LIKE '%Comprar%' THEN 1 ELSE 0 END) as posts_com_comprar
FROM wp_posts 
WHERE post_content LIKE '%creativecopias.com.br%' 
AND post_status = 'publish';
