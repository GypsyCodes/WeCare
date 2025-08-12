#!/usr/bin/env python3
"""
Teste mínimo do FastAPI
Sem dependências do projeto
"""
from fastapi import FastAPI
import uvicorn

# Create minimal app
app = FastAPI(
    title="We Care - Teste Mínimo",
    description="Teste básico sem dependências",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "🎉 FastAPI funcionando!",
        "version": "1.0.0",
        "status": "✅ healthy"
    }

@app.get("/hello")
async def hello():
    """Hello endpoint"""
    return {"message": "Hello from We Care!"}

if __name__ == "__main__":
    print("🚀 Teste mínimo do FastAPI")
    print("📍 Acesse: http://127.0.0.1:8000")
    print("📋 Endpoints: / e /hello")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 