"""
Scheduler Manager - Orquestrador de Jobs Automáticos
Gerencia execução automática de scraping, geração e limpeza
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from loguru import logger

class SchedulerManager:
    """Gerenciador de agendamento de tarefas"""
    
    def __init__(self, base_url: str = "http://localhost:3025"):
        """Inicializa o scheduler"""
        self.base_url = base_url
        self.scheduler = BackgroundScheduler()
        self.job_history = []
        self.is_running = False
        
        # Configurar logging específico
        logger.add(
            "logs/scheduler.log",
            rotation="1 week",
            retention="30 days",
            level="INFO",
            format="{time} | {level} | {message}"
        )
        
        # Configurar listeners de eventos
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        
        logger.info("⏰ Scheduler Manager inicializado")
    
    def _job_executed(self, event):
        """Callback para job executado com sucesso"""
        job_info = {
            'job_id': event.job_id,
            'execution_time': datetime.now(),
            'status': 'success',
            'duration': getattr(event, 'duration', None)
        }
        self.job_history.append(job_info)
        logger.info(f"✅ Job executado: {event.job_id}")
    
    def _job_error(self, event):
        """Callback para job com erro"""
        job_info = {
            'job_id': event.job_id,
            'execution_time': datetime.now(),
            'status': 'error',
            'error': str(event.exception) if event.exception else 'Erro desconhecido'
        }
        self.job_history.append(job_info)
        logger.error(f"❌ Erro no job {event.job_id}: {event.exception}")
    
    def job_scraper(self):
        """
        Job de scraping - extrai produtos do Creative Cópias
        Executa diariamente às 10h
        """
        try:
            logger.info("🕷️ Iniciando job de scraping automático")
            
            # Fazer request para o endpoint de scraping
            response = requests.post(
                f"{self.base_url}/scraper/run",
                timeout=300  # 5 minutos timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Scraping concluído: {result}")
                return result
            else:
                logger.error(f"❌ Erro no scraping: HTTP {response.status_code}")
                return {"status": "error", "code": response.status_code}
                
        except requests.RequestException as e:
            logger.error(f"❌ Erro de conexão no scraping: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"❌ Erro inesperado no scraping: {e}")
            return {"status": "error", "message": str(e)}
    
    def job_generator(self):
        """
        Job de geração COMPLETO - NOVO FLUXO AUTOMATIZADO
        1. Arquiva artigos da semana anterior
        2. Executa scraping de novos produtos
        3. Gera novos artigos automaticamente
        4. Sistema fica pronto para revisão
        """
        try:
            logger.info("🚀 INICIANDO FLUXO COMPLETO AUTOMATIZADO SEMANAL")
            results = {'steps': []}
            
            # PASSO 1: Arquivar artigos da semana anterior
            logger.info("📦 PASSO 1/4: Arquivando artigos da semana anterior...")
            try:
                from src.review.weekly_archive import WeeklyArchiveManager
                archive_manager = WeeklyArchiveManager()
                
                archive_result = archive_manager.archive_previous_week_articles()
                results['steps'].append({
                    'step': 'archive',
                    'status': archive_result.get('status', 'unknown'),
                    'archived_count': archive_result.get('archived_count', 0),
                    'message': f"Arquivados {archive_result.get('archived_count', 0)} artigos"
                })
                
                if archive_result['status'] == 'success':
                    logger.info(f"✅ Arquivamento concluído: {archive_result['archived_count']} artigos")
                else:
                    logger.info(f"ℹ️ Arquivamento: {archive_result.get('message', 'Nenhum artigo para arquivar')}")
                    
            except Exception as e:
                logger.error(f"❌ Erro no arquivamento: {e}")
                results['steps'].append({
                    'step': 'archive',
                    'status': 'error',
                    'message': f"Erro no arquivamento: {str(e)}"
                })
            
            # PASSO 2: Executar scraping de produtos
            logger.info("🕷️ PASSO 2/4: Executando scraping de novos produtos...")
            try:
                scraping_response = requests.post(
                    f"{self.base_url}/scraper/run",
                    headers={'Content-Type': 'application/json'},
                    json={'full_scraping': True},
                    timeout=300  # 5 minutos para scraping
                )
                
                if scraping_response.status_code == 200:
                    # Aguardar scraping completar (verificação periódica)
                    scraping_completed = False
                    wait_time = 0
                    max_wait = 180  # 3 minutos max
                    
                    while not scraping_completed and wait_time < max_wait:
                        time.sleep(10)  # Aguardar 10 segundos
                        wait_time += 10
                        
                        try:
                            stats_response = requests.get(f"{self.base_url}/scraper/stats", timeout=30)
                            if stats_response.status_code == 200:
                                stats = stats_response.json()
                                produtos_processados = stats.get('produtos_processados', 0)
                                
                                if produtos_processados > 0:
                                    scraping_completed = True
                                    logger.info(f"✅ Scraping concluído: {produtos_processados} produtos")
                                    
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao verificar status do scraping: {e}")
                    
                    if scraping_completed:
                        results['steps'].append({
                            'step': 'scraping',
                            'status': 'success',
                            'produtos_encontrados': produtos_processados,
                            'message': f"Encontrados {produtos_processados} produtos"
                        })
                    else:
                        results['steps'].append({
                            'step': 'scraping',
                            'status': 'timeout',
                            'message': "Scraping iniciado mas ainda processando"
                        })
                        
                else:
                    logger.error(f"❌ Erro no scraping: HTTP {scraping_response.status_code}")
                    results['steps'].append({
                        'step': 'scraping',
                        'status': 'error',
                        'message': f"Erro HTTP {scraping_response.status_code}"
                    })
                    
            except Exception as e:
                logger.error(f"❌ Erro no scraping: {e}")
                results['steps'].append({
                    'step': 'scraping',
                    'status': 'error',
                    'message': f"Erro no scraping: {str(e)}"
                })
            
            # PASSO 3: Gerar múltiplos artigos automaticamente
            logger.info("🤖 PASSO 3/4: Gerando artigos automaticamente...")
            try:
                from src.generator.generator_manager import GeneratorManager
                from src.review.review_manager import ReviewManager
                
                generator = GeneratorManager()
                review_manager = ReviewManager()
                
                # Gerar 5 artigos diferentes para a semana
                total_gerados = 0
                total_salvos = 0
                
                for i in range(5):
                    try:
                        logger.info(f"📝 Gerando artigo {i+1}/5...")
                        
                        # CORREÇÃO: Usar geração com produto aleatório diverso
                        article = generator.content_generator.generate_article_from_random_product()
                        
                        if article and article.get('titulo'):
                            total_gerados += 1
                            
                            # Salvar para revisão
                            try:
                                article_id = review_manager.save_article_for_review(article)
                                total_salvos += 1
                                logger.info(f"✅ Artigo {i+1} salvo: ID {article_id}")
                            except ValueError as e:
                                if "duplicado" in str(e):
                                    logger.warning(f"⚠️ Artigo {i+1} duplicado, pulando...")
                                else:
                                    logger.error(f"❌ Erro validação artigo {i+1}: {e}")
                            except Exception as e:
                                logger.error(f"❌ Erro salvar artigo {i+1}: {e}")
                        else:
                            logger.warning(f"⚠️ Falha na geração do artigo {i+1}")
                            
                        # Pequena pausa entre gerações
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"❌ Erro geração artigo {i+1}: {e}")
                        continue
                
                results['steps'].append({
                    'step': 'generation',
                    'status': 'success' if total_salvos > 0 else 'partial',
                    'artigos_gerados': total_gerados,
                    'artigos_salvos': total_salvos,
                    'message': f"Gerados {total_gerados}, salvos {total_salvos}"
                })
                
                logger.info(f"✅ Geração concluída: {total_gerados} gerados, {total_salvos} salvos")
                
            except Exception as e:
                logger.error(f"❌ Erro na geração: {e}")
                results['steps'].append({
                    'step': 'generation',
                    'status': 'error',
                    'message': f"Erro na geração: {str(e)}"
                })
            
            # PASSO 4: Preparar sistema para revisão
            logger.info("📝 PASSO 4/4: Sistema preparado para revisão...")
            try:
                # Obter estatísticas finais
                stats_response = requests.get(f"{self.base_url}/review/stats", timeout=30)
                if stats_response.status_code == 200:
                    review_stats = stats_response.json()
                    pending_count = review_stats.get('statistics', {}).get('pendentes', 0)
                    
                    results['steps'].append({
                        'step': 'preparation',
                        'status': 'success',
                        'artigos_pendentes': pending_count,
                        'message': f"Sistema pronto: {pending_count} artigos aguardando revisão"
                    })
                    
                    logger.info(f"✅ Sistema preparado: {pending_count} artigos aguardando revisão")
                else:
                    results['steps'].append({
                        'step': 'preparation',
                        'status': 'warning',
                        'message': "Sistema preparado, mas não foi possível verificar estatísticas"
                    })
                    
            except Exception as e:
                logger.error(f"❌ Erro na preparação: {e}")
                results['steps'].append({
                    'step': 'preparation',
                    'status': 'error',
                    'message': f"Erro na preparação: {str(e)}"
                })
            
            # Determinar status final
            success_steps = len([s for s in results['steps'] if s['status'] == 'success'])
            total_steps = len(results['steps'])
            
            if success_steps == total_steps:
                final_status = "success"
                final_message = "🎉 FLUXO COMPLETO EXECUTADO COM SUCESSO! Sistema pronto para revisão."
            elif success_steps > 0:
                final_status = "partial"
                final_message = f"⚠️ Fluxo parcialmente concluído: {success_steps}/{total_steps} passos bem-sucedidos"
            else:
                final_status = "error"
                final_message = "❌ Falha no fluxo automatizado"
            
            logger.info(f"🏁 FLUXO FINALIZADO: {final_status.upper()}")
            logger.info(final_message)
            
            return {
                "status": final_status,
                "message": final_message,
                "execution_details": results,
                "summary": {
                    'archived_articles': next((s.get('archived_count', 0) for s in results['steps'] if s['step'] == 'archive'), 0),
                    'products_found': next((s.get('produtos_encontrados', 0) for s in results['steps'] if s['step'] == 'scraping'), 0),
                    'articles_generated': next((s.get('artigos_gerados', 0) for s in results['steps'] if s['step'] == 'generation'), 0),
                    'articles_saved': next((s.get('artigos_salvos', 0) for s in results['steps'] if s['step'] == 'generation'), 0),
                    'pending_review': next((s.get('artigos_pendentes', 0) for s in results['steps'] if s['step'] == 'preparation'), 0)
                }
            }
                
        except Exception as e:
            logger.error(f"❌ Erro crítico no fluxo completo: {e}")
            return {
                "status": "error",
                "message": f"Erro crítico no fluxo automatizado: {str(e)}",
                "execution_time": datetime.now().isoformat()
            }
    
    def setup_jobs(self):
        """Configura todos os jobs agendados"""
        try:
            # Job de scraping - domingos às 10h (semanal)
            self.scheduler.add_job(
                func=self.job_scraper,
                trigger=CronTrigger(day_of_week=6, hour=10, minute=0),  # Domingo = 6
                id='weekly_scraping',
                name='Scraping Semanal Creative Cópias',
                replace_existing=True,
                max_instances=1
            )
            
            # Job de geração - domingos às 10h15 (15 min após scraping)
            self.scheduler.add_job(
                func=self.job_generator,
                trigger=CronTrigger(day_of_week=6, hour=10, minute=15),  # Domingo = 6
                id='weekly_generation',
                name='Geração de Conteúdo Semanal',
                replace_existing=True,
                max_instances=1
            )
            
            # Job de limpeza mensal - primeiro domingo do mês às 2h
            self.scheduler.add_job(
                func=self.job_cleanup,
                trigger=CronTrigger(day_of_week=6, hour=2, minute=0, week=1),  # Primeiro domingo do mês
                id='monthly_cleanup',
                name='Limpeza Mensal de Dados',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info("⏰ Jobs configurados com sucesso:")
            logger.info("  📅 Scraping: Domingos às 10h00 (semanal)")
            logger.info("  🤖 Geração: Domingos às 10h15 (semanal)")
            logger.info("  🧹 Limpeza: Primeiro domingo do mês às 02h00")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar jobs: {e}")
            raise
    
    def job_cleanup(self):
        """
        Job de limpeza - remove dados antigos
        Executa semanalmente aos domingos às 2h
        """
        try:
            logger.info("🧹 Iniciando job de limpeza automática")
            
            cleanup_results = []
            
            # Limpeza do scraper
            try:
                response = requests.post(f"{self.base_url}/scraper/cleanup", timeout=60)
                if response.status_code == 200:
                    cleanup_results.append({"scraper": "success"})
                    logger.info("✅ Limpeza do scraper concluída")
                else:
                    cleanup_results.append({"scraper": "error", "code": response.status_code})
            except Exception as e:
                cleanup_results.append({"scraper": "error", "message": str(e)})
            
            # Limpeza do publisher
            try:
                response = requests.post(f"{self.base_url}/publisher/cleanup", timeout=60)
                if response.status_code == 200:
                    cleanup_results.append({"publisher": "success"})
                    logger.info("✅ Limpeza do publisher concluída")
                else:
                    cleanup_results.append({"publisher": "error", "code": response.status_code})
            except Exception as e:
                cleanup_results.append({"publisher": "error", "message": str(e)})
            
            logger.info(f"🧹 Limpeza concluída: {cleanup_results}")
            return {"status": "completed", "results": cleanup_results}
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")
            return {"status": "error", "message": str(e)}
    
    def start(self):
        """Inicia o scheduler"""
        try:
            if not self.is_running:
                self.setup_jobs()
                self.scheduler.start()
                self.is_running = True
                logger.info("🚀 Scheduler iniciado com sucesso")
            else:
                logger.warning("⚠️ Scheduler já está rodando")
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar scheduler: {e}")
            raise
    
    def stop(self):
        """Para o scheduler"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("🛑 Scheduler parado")
            else:
                logger.warning("⚠️ Scheduler já está parado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao parar scheduler: {e}")
    
    def pause(self):
        """Pausa todos os jobs"""
        try:
            self.scheduler.pause()
            logger.info("⏸️ Scheduler pausado")
            return {"status": "paused"}
        except Exception as e:
            logger.error(f"❌ Erro ao pausar scheduler: {e}")
            return {"status": "error", "message": str(e)}
    
    def resume(self):
        """Resume todos os jobs"""
        try:
            self.scheduler.resume()
            logger.info("▶️ Scheduler resumido")
            return {"status": "resumed"}
        except Exception as e:
            logger.error(f"❌ Erro ao resumir scheduler: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_complete_workflow(self):
        """
        Executa o fluxo completo: versão ultrarrápida e robusta
        Foca na geração de artigos para demonstração
        """
        try:
            logger.info("🚀 Iniciando fluxo completo: modo super rápido")
            workflow_results = {}
            
            # Importar os managers diretamente
            try:
                from src.generator.generator_manager import GeneratorManager
                from src.review.review_manager import ReviewManager
                
                # Pular scraping por enquanto - ir direto para geração
                logger.info("📡 Passo 1/3: Pulando scraping (modo rápido)...")
                workflow_results['scraping'] = {
                    'status': 'skipped',
                    'message': 'Scraping pulado para demonstração rápida'
                }
                
                # Passo 2: Executar geração direta
                logger.info("🤖 Passo 2/3: Executando geração direta...")
                generator = GeneratorManager()
                
                # Gerar múltiplos artigos de teste
                articles_generated = 0
                test_articles = []
                
                # Tentar gerar 3 artigos diferentes
                for i in range(3):
                    try:
                        logger.info(f"📄 Gerando artigo {i+1}/3...")
                        # CORREÇÃO: Usar geração com produto aleatório diverso
                        test_article = generator.content_generator.generate_article_from_random_product()
                        if test_article:
                            test_articles.append(test_article)
                            articles_generated += 1
                            logger.info(f"✅ Artigo {i+1} gerado com sucesso")
                        else:
                            logger.warning(f"⚠️ Falha na geração do artigo {i+1}")
                    except Exception as e:
                        logger.error(f"❌ Erro na geração do artigo {i+1}: {e}")
                        continue
                
                # Passo 3: Salvar para revisão
                logger.info("📝 Passo 3/3: Salvando artigos para revisão...")
                saved_articles = []
                
                for idx, article in enumerate(test_articles):
                    try:
                        review_manager = ReviewManager()
                        article_id = review_manager.save_article_for_review(article)
                        saved_articles.append(article_id)
                        logger.info(f"✅ Artigo {idx+1} salvo para revisão com ID: {article_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao salvar artigo {idx+1}: {e}")
                        continue
                
                workflow_results['generation'] = {
                    'status': 'success' if articles_generated > 0 else 'no_articles',
                    'articles_generated': articles_generated,
                    'articles_saved': len(saved_articles)
                }
                
                workflow_results['review'] = {
                    'status': 'success' if saved_articles else 'error',
                    'saved_articles': saved_articles
                }
                
            except ImportError as ie:
                logger.error(f"❌ Erro de importação nos módulos: {ie}")
                workflow_results = {
                    'error': f"Módulos necessários não disponíveis: {str(ie)}"
                }
                articles_generated = 0
                saved_articles = []
            
            # Determinar status final
            if articles_generated > 0:
                final_status = "success"
                message = f"🎉 Processo completo executado! {articles_generated} artigo(s) gerado(s) e {len(saved_articles)} salvo(s) para revisão."
            else:
                final_status = "error"
                message = "❌ Nenhum artigo foi gerado"
            
            logger.info(f"✅ Fluxo completo finalizado: {final_status}")
            
            return {
                "status": final_status,
                "message": message,
                "results": workflow_results,
                "articles_generated": articles_generated,
                "articles_saved": len(saved_articles),
                "execution_time": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"❌ Erro no fluxo completo: {e}")
            return {
                "status": "error",
                "message": f"Erro no fluxo completo: {str(e)}",
                "execution_time": datetime.now().isoformat()
            }

    def run_job_manually(self, job_id: str):
        """Executa um job manualmente"""
        try:
            if job_id == 'weekly_scraping':
                result = self.job_scraper()
            elif job_id == 'weekly_generation':
                result = self.job_generator()
            elif job_id == 'monthly_cleanup':
                result = self.job_cleanup()
            elif job_id == 'complete_workflow':
                result = self.run_complete_workflow()
            else:
                return {"status": "error", "message": f"Job '{job_id}' não encontrado"}
            
            logger.info(f"🔧 Job '{job_id}' executado manualmente")
            return {"status": "executed", "job_id": job_id, "result": result}
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar job '{job_id}': {e}")
            return {"status": "error", "message": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do scheduler e jobs"""
        try:
            jobs_info = []
            
            if self.is_running:
                for job in self.scheduler.get_jobs():
                    next_run = job.next_run_time
                    jobs_info.append({
                        'id': job.id,
                        'name': job.name,
                        'next_run': next_run.isoformat() if next_run else None,
                        'trigger': str(job.trigger),
                        'func_name': job.func.__name__ if hasattr(job, 'func') else 'N/A'
                    })
            
            # Histórico das últimas 10 execuções
            recent_history = sorted(
                self.job_history, 
                key=lambda x: x['execution_time'], 
                reverse=True
            )[:10]
            
            return {
                'is_running': self.is_running,
                'scheduler_state': self.scheduler.state if hasattr(self.scheduler, 'state') else 'unknown',
                'jobs_count': len(jobs_info),
                'jobs': jobs_info,
                'recent_executions': [
                    {
                        **execution,
                        'execution_time': execution['execution_time'].isoformat()
                    } for execution in recent_history
                ],
                'base_url': self.base_url,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {e}")
            return {
                'is_running': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_next_executions(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Retorna próximas execuções nas próximas X horas"""
        try:
            if not self.is_running:
                return []
            
            now = datetime.now()
            future_limit = now + timedelta(hours=hours)
            
            executions = []
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time
                if next_run and now <= next_run <= future_limit:
                    executions.append({
                        'job_id': job.id,
                        'job_name': job.name,
                        'next_run': next_run.isoformat(),
                        'hours_until': (next_run - now).total_seconds() / 3600
                    })
            
            return sorted(executions, key=lambda x: x['next_run'])
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter próximas execuções: {e}")
            return [] 