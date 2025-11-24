"""
API REST para análisis de código C4

⚠️ NOTA: Esta API está simplificada y solo expone funcionalidad básica.
   La API avanzada con Knowledge Graphs fue deprecada (ver main.py.deprecated).
   
   Para uso completo del sistema, ejecuta: streamlit run app.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Agente C4 - Code Analysis API",
    description="API REST para análisis de código y generación de diagramas C4",
    version="4.0.0"
)


@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "Agente C4 - Code Analysis API",
        "version": "4.0.0",
        "status": "online",
        "note": "Para uso completo, usar interfaz Streamlit: streamlit run app.py",
        "endpoints": {
            "health": "GET /health - Estado del servicio",
            "root": "GET / - Este mensaje"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica el estado del servicio"""
    return {
        "status": "healthy",
        "service": "code-analysis-api",
        "version": "4.0.0"
    }


# Futuros endpoints pueden agregarse aquí si se necesitan
# Por ahora, la funcionalidad principal está en app.py (Streamlit)
