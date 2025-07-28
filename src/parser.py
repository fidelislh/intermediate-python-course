import re

def parsear_questoes(texto: str) -> list[dict]:
    """
    Analisa o texto extraído de um PDF e o estrutura em uma lista de questões.
    """
    questoes = []
    # Regex para encontrar cada bloco de questão
    blocos_questoes = re.split(r'(?=\d+\s*–)', texto)[1:]

    for bloco in blocos_questoes:
        try:
            # Extrair número da questão
            numero_match = re.match(r'(\d+)\s*–', bloco)
            if not numero_match:
                continue
            numero = numero_match.group(1)

            # O resto é conteúdo
            conteudo = bloco[numero_match.end():].strip()

            # Dividir o conteúdo em linhas para facilitar o processamento
            linhas = [linha.strip() for linha in conteudo.split('\n') if linha.strip()]

            enunciado_linhas = []
            alternativas_linhas = []
            capturando_enunciado = True

            for linha in linhas:
                if re.match(r'\([A-E]\)', linha, re.IGNORECASE):
                    capturando_enunciado = False

                if capturando_enunciado:
                    enunciado_linhas.append(linha)
                else:
                    alternativas_linhas.append(linha)

            enunciado = " ".join(enunciado_linhas)

            # Agrupar alternativas que podem ter quebras de linha
            alternativas_agrupadas = []
            temp_alt = ""
            for linha in alternativas_linhas:
                if re.match(r'\([A-E]\)', linha, re.IGNORECASE):
                    if temp_alt:
                        alternativas_agrupadas.append(temp_alt.strip())
                    temp_alt = linha
                else:
                    temp_alt += " " + linha
            if temp_alt:
                alternativas_agrupadas.append(temp_alt.strip())

            # Extrair gabarito e explicação (se existirem)
            gabarito = ""
            explicacao = "Nenhuma explicação fornecida."
            # (A lógica para gabarito e explicação pode ser adicionada aqui se o formato for consistente)

            topico = "TÓPICO A SER DEFINIDO"

            if enunciado and alternativas_agrupadas:
                questoes.append({
                    "numero": numero,
                    "topico": topico,
                    "enunciado": enunciado,
                    "alternativas": alternativas_agrupadas,
                    "gabarito": gabarito,
                    "explicacao": explicacao,
                })
        except Exception as e:
            print(f"Erro ao parsear bloco de questão: {e}")
            continue

    return questoes
