# src/utils/text_normalizer.py

def normalizar_texto_banco(valor):
    """
    Corrige APENAS mojibake (latin1/cp1252 lido como utf-8).
    NÃO tenta recuperar texto que já virou � (replacement char).
    """

    if valor is None:
        return None

    # Bytes: decode certo, uma vez só
    if isinstance(valor, bytes):
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                return valor.decode(enc)
            except UnicodeDecodeError:
                pass
        return valor.decode("latin-1", errors="replace")

    if not isinstance(valor, str):
        return str(valor)

    # Se já tem replacement char, NÃO mexe
    if "�" in valor:
        return valor

    # Mojibake clássico
    if any(x in valor for x in ("Ã", "Â")):
        try:
            return valor.encode("latin-1").decode("utf-8")
        except UnicodeError:
            try:
                return valor.encode("cp1252").decode("utf-8")
            except UnicodeError:
                return valor

    return valor

