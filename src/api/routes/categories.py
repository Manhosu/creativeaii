#!/usr/bin/env python3
"""
Categories API Routes
Endpoints para gerenciar categorias ativas do sistema
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

from ...config.active_categories_manager import ActiveCategoriesManager

router = APIRouter(prefix="/categories", tags=["categories"])

# Models
class CategoryUpdateModel(BaseModel):
    is_active: bool

class CategoryPriorityModel(BaseModel):
    priority: int

class CategoriesBatchUpdateModel(BaseModel):
    categories: Dict[str, bool]  # category_key -> is_active

# Inicializar manager
categories_manager = ActiveCategoriesManager()

@router.get("/", summary="Listar todas as categorias")
async def get_all_categories():
    """Retorna todas as categorias (ativas e inativas)"""
    try:
        categories = categories_manager.get_all_categories()
        summary = categories_manager.get_categories_summary()
        
        return {
            "status": "success",
            "categories": categories,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", summary="Listar categorias ativas")
async def get_active_categories():
    """Retorna apenas categorias ativas ordenadas por prioridade"""
    try:
        categories = categories_manager.get_active_categories()
        
        return {
            "status": "success",
            "active_categories": categories,
            "count": len(categories)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar categorias ativas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", summary="Resumo das categorias")
async def get_categories_summary():
    """Retorna resumo estatístico das categorias"""
    try:
        summary = categories_manager.get_categories_summary()
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{category_key}/status", summary="Atualizar status da categoria")
async def update_category_status(category_key: str, update: CategoryUpdateModel):
    """Ativa ou desativa uma categoria específica"""
    try:
        success = categories_manager.update_category_status(category_key, update.is_active)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Categoria '{category_key}' não encontrada")
        
        status_text = "ativada" if update.is_active else "desativada"
        
        return {
            "status": "success",
            "message": f"Categoria '{category_key}' {status_text} com sucesso",
            "category_key": category_key,
            "is_active": update.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{category_key}/priority", summary="Atualizar prioridade da categoria")
async def update_category_priority(category_key: str, update: CategoryPriorityModel):
    """Atualiza a prioridade de processamento de uma categoria"""
    try:
        success = categories_manager.update_category_priority(category_key, update.priority)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Categoria '{category_key}' não encontrada")
        
        return {
            "status": "success",
            "message": f"Prioridade da categoria '{category_key}' atualizada para {update.priority}",
            "category_key": category_key,
            "priority": update.priority
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar prioridade da categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/batch", summary="Atualização em lote")
async def update_categories_batch(update: CategoriesBatchUpdateModel):
    """Atualiza status de múltiplas categorias em uma operação"""
    try:
        success = categories_manager.update_categories_batch(update.categories)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erro na atualização em lote")
        
        active_count = sum(1 for active in update.categories.values() if active)
        total_count = len(update.categories)
        
        return {
            "status": "success",
            "message": f"Atualização em lote concluída: {active_count}/{total_count} categorias ativas",
            "updated_categories": update.categories,
            "active_count": active_count,
            "total_count": total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na atualização em lote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/discover", summary="Descobrir novas categorias")
async def discover_categories(background_tasks: BackgroundTasks):
    """Descobre automaticamente novas categorias do site"""
    try:
        # Executar descoberta em background para não bloquear
        new_categories = await categories_manager.discover_and_update_categories()
        
        return {
            "status": "success",
            "message": f"Descoberta concluída: {new_categories} novas categorias encontradas",
            "new_categories_count": new_categories
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na descoberta de categorias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{category_key}", summary="Detalhes da categoria")
async def get_category_details(category_key: str):
    """Retorna detalhes de uma categoria específica"""
    try:
        categories = categories_manager.get_all_categories()
        category = next((cat for cat in categories if cat['category_key'] == category_key), None)
        
        if not category:
            raise HTTPException(status_code=404, detail=f"Categoria '{category_key}' não encontrada")
        
        return {
            "status": "success",
            "category": category
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{category_key}/is-active", summary="Verificar se categoria está ativa")
async def check_category_active(category_key: str):
    """Verifica rapidamente se uma categoria está ativa"""
    try:
        is_active = categories_manager.is_category_active(category_key)
        
        return {
            "status": "success",
            "category_key": category_key,
            "is_active": is_active
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar categoria '{category_key}': {e}")
        raise HTTPException(status_code=500, detail=str(e)) 