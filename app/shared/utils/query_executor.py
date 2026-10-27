from fastapi import HTTPException
from app.shared.database.connection_firebird import get_connection_firebird
from app.shared.utils.text_normalizer import normalizar_texto_banco
from datetime import date, datetime


async def execute_query(query: str, params: tuple = None):
    conn = None

    try:
        conn = get_connection_firebird()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        columns = [desc[0].lower() for desc in cursor.description]

        results = []

        for row in cursor.fetchall():
            item = {}

            for i, col in enumerate(columns):
                val = row[i]

                if val is None:
                    item[col] = None

                elif isinstance(val, (datetime, date)):
                    item[col] = val.isoformat()

                elif isinstance(val, float):
                    item[col] = round(val, 2)

                else:
                    item[col] = normalizar_texto_banco(val)

            results.append(item)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if conn:
            conn.close()