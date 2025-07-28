import os
from src.extractor import extrair_texto_de_pdf
from src.parser import parsear_questoes
from src.generator import gerar_html_final

PDFS_DIR = 'pdfs'
TEMPLATES_DIR = 'templates'
OUTPUT_DIR = 'output'
TEMPLATE_NAME = 'base.html'

def main():
    """
    Script principal para processar todos os PDFs e gerar os arquivos HTML.
    """
    # Garante que o diretório de saída exista
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    template_path = os.path.join(TEMPLATES_DIR, TEMPLATE_NAME)

    # Verifica se o template existe
    if not os.path.exists(template_path):
        print(f"Erro: Arquivo de template não encontrado em {template_path}")
        return

    # Encontra todos os arquivos PDF ou TXT no diretório
    files_to_process = [f for f in os.listdir(PDFS_DIR) if f.lower().endswith(('.pdf', '.txt'))]

    if not files_to_process:
        print(f"Nenhum arquivo PDF ou TXT encontrado no diretório '{PDFS_DIR}'.")
        print("Por favor, adicione seus arquivos e tente novamente.")
        return

    print(f"Encontrados {len(files_to_process)} arquivos para processar...")

    for filename in files_to_process:
        file_path = os.path.join(PDFS_DIR, filename)
        print(f"\nProcessando '{file_path}'...")

        texto_extraido = ""
        if filename.lower().endswith('.pdf'):
            # 1. Extrair texto do PDF
            texto_extraido = extrair_texto_de_pdf(file_path)
        elif filename.lower().endswith('.txt'):
            # 1. Ler texto do TXT
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    texto_extraido = f.read()
            except Exception as e:
                print(f"Erro ao ler o arquivo de texto {file_path}: {e}")
                continue

        if not texto_extraido:
            print(f"Não foi possível extrair ou ler o texto de '{file_path}'. Pulando.")
            continue

        # 2. Parsear questões
        questoes_estruturadas = parsear_questoes(texto_extraido)
        if not questoes_estruturadas:
            print(f"Nenhuma questão encontrada ou parseada em '{file_path}'. Pulando.")
            continue

        print(f"Encontradas {len(questoes_estruturadas)} questões em '{filename}'.")

        # 3. Gerar HTML
        output_filename = os.path.splitext(filename)[0] + '.html'
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        gerar_html_final(questoes_estruturadas, template_path, output_path)

    print("\nProcessamento concluído.")

if __name__ == '__main__':
    main()
