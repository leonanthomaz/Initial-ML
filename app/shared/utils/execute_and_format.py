# src/shared/utils/execute_and_format.py

from http.client import HTTPException

from app.shared.database.connection_firebird import get_connection_firebird
from app.shared.utils.text_normalizer import normalizar_texto_banco

async def execute_and_format(query: str):
    """Executa query e formata resultado"""
    
    conn = None
    try:
        conn = get_connection_firebird()
        cursor = conn.cursor()
        cursor.execute(query)
        
        columns = [desc[0].strip() for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            item = {}
            for i, col in enumerate(columns):
                valor = row[i]
                if hasattr(valor, 'isoformat'):
                    item[col] = valor.isoformat()
                elif valor is None:
                    item[col] = None
                else:
                    item[col] = str(normalizar_texto_banco(valor))
            results.append(item)
        
        conn.close()
        
        return {
            "status": "success",
            "query": query,
            "total_returned": len(results),
            "data": results
        }
        
    except Exception as e:
        if conn:
            conn.close()
        raise HTTPException(500, detail=str(e))