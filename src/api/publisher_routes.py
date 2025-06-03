@router.post("/publish")
async def publish_article(publication_data: dict):
    """
    Publica artigo no WordPress
    """
    try:
        # CORREÇÃO URGENTE: Validação mais robusta dos dados
        article_id = publication_data.get('article_id')
        
        # Validação básica
        if not article_id:
            logger.error("❌ ERRO 400: article_id não fornecido")
            return {
                'success': False,
                'error': 'Campo article_id é obrigatório',
                'error_code': 'MISSING_ARTICLE_ID'
            }
        
        # Tentar converter para int se for string
        try:
            article_id = int(article_id)
        except (ValueError, TypeError):
            logger.error(f"❌ ERRO 400: article_id inválido: {article_id}")
            return {
                'success': False,
                'error': f'article_id deve ser um número válido. Recebido: {article_id}',
                'error_code': 'INVALID_ARTICLE_ID'
            }
        
        publish_immediately = publication_data.get('publish_immediately', True)
        scheduled_date = publication_data.get('scheduled_date')
        
        logger.info(f"📤 Iniciando publicação do artigo ID {article_id}")
        
        # Buscar dados do artigo no sistema de revisão
        review_manager = ReviewManager()
        
        # CORREÇÃO: Verificar se artigo existe antes de tentar publicar
        article_data = review_manager.get_article_by_id(article_id)
        
        if not article_data:
            logger.error(f"❌ ERRO 404: Artigo {article_id} não encontrado")
            return {
                'success': False,
                'error': f'Artigo com ID {article_id} não encontrado no sistema',
                'error_code': 'ARTICLE_NOT_FOUND'
            }
        
        # Verificar se artigo está aprovado
        if article_data.get('status') != 'aprovado':
            logger.warning(f"⚠️ Artigo {article_id} não está aprovado (status: {article_data.get('status')})")
            return {
                'success': False,
                'error': f'Artigo deve estar aprovado para publicação. Status atual: {article_data.get("status")}',
                'error_code': 'ARTICLE_NOT_APPROVED'
            }
        
        # Inicializar o publisher
        publication_manager = PublicationManager()
        
        # CORREÇÃO: Try-catch mais específico para diferentes tipos de erro
        try:
            # Tentar publicação
            result = publication_manager.publish_article(
                article_data=article_data,
                publish_immediately=publish_immediately,
                scheduled_date=scheduled_date
            )
            
            if result.get('success'):
                logger.info(f"✅ Artigo {article_id} publicado com sucesso")
                return {
                    'success': True,
                    'message': 'Artigo publicado com sucesso!',
                    'wp_post_id': result.get('wp_post_id'),
                    'wp_url': result.get('wp_url'),
                    'status': result.get('status'),
                    'note': result.get('note'),
                    'publication_id': result.get('publication_id')
                }
            else:
                logger.error(f"❌ Falha na publicação do artigo {article_id}: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Erro desconhecido na publicação'),
                    'error_code': 'PUBLICATION_FAILED'
                }
                
        except Exception as pub_error:
            logger.error(f"❌ Exceção durante publicação do artigo {article_id}: {pub_error}")
            return {
                'success': False,
                'error': f'Erro interno na publicação: {str(pub_error)}',
                'error_code': 'INTERNAL_PUBLICATION_ERROR'
            }
        
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO na rota de publicação: {e}")
        return {
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}',
            'error_code': 'INTERNAL_SERVER_ERROR'
        } 