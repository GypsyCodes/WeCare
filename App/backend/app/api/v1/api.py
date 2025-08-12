"""
Main API router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, usuarios, escalas, escala_usuarios, checkins, documentos, relatorios, estabelecimentos, setores

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(estabelecimentos.router, prefix="/estabelecimentos", tags=["estabelecimentos"])
api_router.include_router(escalas.router, prefix="/escalas", tags=["escalas"])
api_router.include_router(escala_usuarios.router, prefix="/escalas", tags=["escala-usuarios"])
api_router.include_router(setores.router, prefix="/setores", tags=["setores"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["checkins"])
api_router.include_router(documentos.router, prefix="/documentos", tags=["documentos"])
api_router.include_router(relatorios.router, prefix="/relatorios", tags=["relatorios"]) 