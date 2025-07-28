from collections import defaultdict

def gerar_html_questao(questao: dict, questao_index: int, total_questoes: int) -> str:
    """Gera o bloco HTML para uma única questão."""

    alternativas_html = ""
    for alt in questao["alternativas"]:
        # Remove o prefixo (a), b), etc.) para comparar com o gabarito
        letra_alternativa = alt.strip()[0].lower()
        if letra_alternativa == questao["gabarito"]:
            alternativas_html += f'<b>{alt}</b><br>\n'
        else:
            alternativas_html += f'{alt}<br>\n'

    return f"""
    <!-- Questão {questao['numero']} -->
    <div class="slide-container bg-white flex flex-col p-10">
        <div class="recycling-border w-full h-3 mb-6"></div>
        <div class="topico-title">
            <h1 class="text-3xl font-bold text-white text-center">{questao['topico']}</h1>
        </div>
        <div class="mb-6">
            <h1 class="text-4xl font-bold text-green-800">Questão {questao['numero']}</h1>
            <div class="w-32 h-1 bg-green-600 mt-2"></div>
        </div>
        <div class="flex-1">
            <div class="questao-box">
                <h2 class="text-2xl font-semibold text-blue-900 mb-2">Questão</h2>
                <p class="text-gray-700">{questao['enunciado']}</p>
            </div>
            <div class="resposta-box">
                <h2 class="text-2xl font-semibold text-blue-900 mb-2">Resposta</h2>
                <p class="text-gray-700">{alternativas_html}</p>
            </div>
            <div class="explicacao-box">
                <h2 class="text-2xl font-semibold text-blue-900 mb-2">Explicação</h2>
                <p class="text-gray-700">{questao['explicacao']}</p>
            </div>
        </div>
        <div class="mt-auto pt-6 flex justify-between items-center">
            <div class="recycling-border w-full h-3"></div>
            <div class="absolute bottom-4 right-10 text-gray-600 text-sm">{questao_index}/{total_questoes}</div>
        </div>
    </div>
    """

def gerar_html_final(questoes: list[dict], template_path: str, output_path: str):
    """
    Gera o arquivo HTML final com todas as questões.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        questoes_html = ""
        total_questoes = len(questoes)

        # Agrupar questões por tópico para exibição
        questoes_por_topico = defaultdict(list)
        for q in questoes:
            questoes_por_topico[q['topico']].append(q)

        current_questao_index = 2 # Começa em 2 para contar com a página de título
        for topico, lista_questoes in questoes_por_topico.items():
            for questao in lista_questoes:
                questoes_html += gerar_html_questao(questao, current_questao_index, total_questoes + 1)
                current_questao_index += 1

        final_html = template_html.replace('<!-- CONTENT -->', questoes_html)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

        print(f"Arquivo HTML gerado com sucesso em: {output_path}")

    except Exception as e:
        print(f"Erro ao gerar o HTML final: {e}")
