import fitz  # PyMuPDF

def extrair_texto_de_pdf(caminho_pdf: str) -> str:
    """
    Extrai todo o texto de um arquivo PDF.

    Args:
        caminho_pdf: O caminho para o arquivo PDF.

    Returns:
        O conteúdo de texto do PDF como uma string.
    """
    try:
        doc = fitz.open(caminho_pdf)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        doc.close()
        return texto
    except Exception as e:
        print(f"Erro ao extrair texto do PDF {caminho_pdf}: {e}")
        return ""
