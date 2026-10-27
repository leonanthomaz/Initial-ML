# app/modules/analysis/controller/chat_controller.py

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import httpx
from app.core.config.settings import Configuration
from app.modules.analysis.models.groq_model import GroqChatRequest
from app.shared.utils.retornar_timestamp import get_current_timestamp

class ChatController(APIRouter):
    """Controller para operações com Assistente"""
    
    def __init__(self):
        super().__init__()
        self.config = Configuration()
        self.logger = logging.getLogger(__name__)

        # Health check
        self.add_api_route(
            path="/health",
            endpoint=self.health_check,
            methods=["GET"],
            summary="Health check"
        )
        
        # Chat
        self.add_api_route(
            path="/chat",
            endpoint=self.chat,
            methods=["POST"],
            summary="Envia mensagem para IA via Assistente"
        )
        
        self.add_api_route(
            path="/models",
            endpoint=self.list_models,
            methods=["GET"],
            summary="Lista modelos disponíveis no Groq"
        )
        
    
    # ============ HEALTH ============
    def health_check(self) -> Dict[str, str]:
        return {
            "status": "ONLINE",
            "service": "API ASSISTENTE",
            "timestamp": get_current_timestamp()
        }
    
    async def chat(self, request: GroqChatRequest) -> Dict:
        """Endpoint principal para conversar com modelos Groq"""
        try:
            # Pega variáveis do .env
            api_key = self.config.groq_api_key
            default_model = self.config.groq_model or "llama-3.1-8b-instant"
            url = self.config.groq_url or "https://api.groq.com/openai/v1/chat/completions"
            
            model = request.model or default_model
            
            # Prepara payload no formato OpenAI (compatível com Groq)
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": request.message}
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": request.stream
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            self.logger.info(f"Groq - Enviando requisição - Modelo: {model}")
            self.logger.debug(f"Payload: {payload}")
            
            # Faz a requisição
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            # Extrai resposta (formato OpenAI)
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Estatísticas de velocidade (Groq é famoso pela velocidade)
            usage = data.get("usage", {})
            speed_info = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "estimated_speed": "~560 tokens/seg" if "8b" in model.lower() else "~280 tokens/seg"
            }
            
            self.logger.info(f"Groq - Resposta recebida - {speed_info['total_tokens']} tokens")
            
            return {
                "success": True,
                "response": content,
                "model": model,
                "usage": speed_info,
                "timestamp": get_current_timestamp(),
                "provider": "groq"
            }
            
        except httpx.TimeoutException:
            self.logger.error("Groq - Timeout na requisição")
            raise HTTPException(status_code=504, detail="Tempo limite excedido")
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Groq - Erro HTTP: {e.response.status_code}")
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                error_detail = error_json.get("error", {}).get("message", str(e))
            except:
                pass
            raise HTTPException(
                status_code=e.response.status_code, 
                detail=f"Erro na API Groq: {error_detail}"
            )
        except Exception as e:
            self.logger.error(f"Groq - Erro inesperado: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def list_models(self) -> Dict:
        """Lista todos os modelos disponíveis no Groq"""
        try:
            api_key = self.config.groq_api_key
            url = "https://api.groq.com/openai/v1/models"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            models = data.get("data", [])
            
            # Filtra e organiza modelos relevantes
            model_list = []
            for model in models:
                model_id = model.get("id", "")
                # Só mostra modelos que parecem úteis (filtra os de segurança)
                if any(keyword in model_id for keyword in ["llama", "gpt-oss", "qwen", "whisper"]):
                    model_list.append({
                        "id": model_id,
                        "created": model.get("created"),
                        "owned_by": model.get("owned_by", "groq")
                    })
            
            return {
                "success": True,
                "total_models": len(model_list),
                "models": model_list,
                "timestamp": get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao listar modelos: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
   