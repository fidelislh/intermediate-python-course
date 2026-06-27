import asyncio
import edge_tts
from pydub import AudioSegment
import re
import os
import argparse
import sys
import shutil

def check_ffmpeg():
    """
    Checks if ffmpeg is installed and available in the system path.
    """
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is not installed or not in the system path.")
        print("Please install ffmpeg to use this script (e.g., 'sudo apt install ffmpeg' or 'brew install ffmpeg').")
        return False
    return True

def sanitize_filename(text):
    """
    Sanitizes a string to be used as a filename.
    """
    text = text.lower()
    # Replace common accented characters
    import unicodedata
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9_ -]', '', text)
    text = re.sub(r'[\s-]+', '_', text).strip('_')
    return text

def limpar_texto(fala):
    """
    Removes emotion and tone markers like [rindo], [didática], etc.
    """
    return re.sub(r'\[[^\]]*\]', '', fala).strip()

def split_dialogo_by_podcast(full_dialogo):
    """
    Splits a large text into individual podcast segments based on titles.
    """
    podcasts = []
    # Matches "Podcast X – Title"
    segments = re.split(r'(Podcast \d+\s*–\s*[^\n]+)', full_dialogo)

    segments = [s.strip() for s in segments if s.strip()]

    current_title = None
    for segment in segments:
        if re.match(r'Podcast \d+\s*–\s*[^\n]+', segment):
            current_title = segment
        elif current_title:
            podcasts.append({
                'title': current_title,
                'content': current_title + "\n" + segment
            })
            current_title = None

    # If no podcasts were split (maybe no titles), return the whole thing as one
    if not podcasts and full_dialogo.strip():
        podcasts.append({
            'title': 'Podcast_Generated',
            'content': full_dialogo
        })

    return podcasts

class PodcastGenerator:
    def __init__(self, voice_joe="pt-BR-AntonioNeural", voice_jane="pt-BR-FranciscaNeural", output_dir="output"):
        self.voices = {
            'JOE': voice_joe,
            'JANE': voice_jane
        }
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.temp_dir = "temp_audio"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def parse_dialogue(self, content):
        """
        Parses the dialogue into a list of (character, text) tuples.
        """
        falas = []
        linhas = content.strip().split('\n')
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue

            # Match JOE: or JANE: (case insensitive)
            match = re.match(r'^(JOE|JANE):\s*(.*)', linha, re.IGNORECASE)
            if match:
                personagem = match.group(1).upper()
                texto_fala = match.group(2).strip()

                texto_limpo = limpar_texto(texto_fala)
                if texto_limpo:
                    falas.append((personagem, texto_limpo))
            else:
                # Handle lines that might be sound effects or other markers
                # for now we just log them if they are in []
                if linha.startswith('[') and linha.endswith(']'):
                    print(f"Skipping sound effect: {linha}")
                continue
        return falas

    async def generate_audio_segments(self, falas, podcast_id):
        """
        Generates audio for each line of dialogue asynchronously.
        """
        tasks = []
        segment_files = []

        for i, (personagem, texto) in enumerate(falas):
            voice = self.voices.get(personagem, "pt-BR-FranciscaNeural")
            temp_file = os.path.join(self.temp_dir, f"segment_{podcast_id}_{i}.mp3")
            segment_files.append(temp_file)

            communicate = edge_tts.Communicate(texto, voice)
            tasks.append(communicate.save(temp_file))

        await asyncio.gather(*tasks)
        return segment_files

    def stitch_audio(self, segment_files, output_filename):
        """
        Combines individual audio segments into a single file.
        """
        combined = AudioSegment.empty()
        silence = AudioSegment.silent(duration=500) # 500ms silence between turns

        for i, file in enumerate(segment_files):
            segment = AudioSegment.from_mp3(file)
            combined += segment
            if i < len(segment_files) - 1:
                combined += silence

        output_path = os.path.join(self.output_dir, output_filename)
        combined.export(output_path, format="mp3")
        print(f"Generated: {output_path}")

        # Clean up temp files
        for file in segment_files:
            try:
                os.remove(file)
            except OSError:
                pass

async def main():
    if not check_ffmpeg():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Generate podcasts from text dialogues.")
    parser.add_argument("--input", "-i", type=str, help="Path to the input text file.")
    parser.add_argument("--output", "-o", type=str, default="output", help="Output directory.")
    parser.add_argument("--joe-voice", type=str, default="pt-BR-AntonioNeural", help="Voice for JOE.")
    parser.add_argument("--jane-voice", type=str, default="pt-BR-FranciscaNeural", help="Voice for JANE.")

    args = parser.parse_args()

    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input file {args.input} not found.")
            sys.exit(1)
        with open(args.input, 'r', encoding='utf-8') as f:
            dialogo_texto = f.read()
    else:
        # Default text from the request if no input file is provided
        dialogo_texto = """
Podcast 11 – Árvores caducifólias no cerrado
[Som de folhas secas caindo e vento]
JOE: [brincalhão] Jane, você já ouviu falar em árvore que fica pelada no inverno? Não, não é piada…
JANE: [rindo] Quase isso, Joe! A pergunta é: no cerrado goiano, com aquela seca braba, as árvores caducifólias fazem o quê? Caducifólia significa…
JOE: [empolgado] Aposto que é árvore que não perde folha, tipo sempre-verde! Letra A!
JANE: [firme] Errou feio! Caducifólia vem do latim cadere = cair. Essas árvores perdem as folhas na época da seca para economizar água. Resposta certa: letra B.
JOE: [fingindo decepção] Puxa, então meu ipê aqui no quintal que fica nu no inverno é caducifólio?
JANE: [didática] Exato! E essas plantas que se adaptam à seca têm um nome especial: xerófilas. Aliás, isso já é a próxima questão…
JOE: [motivacional] Anota aí, ouvinte: caducifólia = perde folha na seca. Não erre igual eu!
[Som de folhas – fade]

Podcast 12 – Plantas xerófilas do cerrado
[Som de cacto estalando]
JOE: [curioso] Jane, a seca no cerrado dura quase 6 meses. Como as plantas sobrevivem? A UFG perguntou o nome delas…
JANE: [vibrante] São as xerófilas! Do grego xeros = seco, philos = amigo. Amigas da seca. Resposta letra B.
JOE: [provocativo] E se eu marcar hidrófilas? Água…
JANE: [rindo] Aí você estaria falando de planta que ama água, tipo aguapé. No cerrado, é xerófila mesmo.
JOE: [motivacional] Dica de mestre: lembre de “xerox” – seca. Xerófila = seca. E não erre na prova!
[Som de estalo – fade]
"""

    podcasts = split_dialogo_by_podcast(dialogo_texto)
    generator = PodcastGenerator(voice_joe=args.joe_voice, voice_jane=args.jane_voice, output_dir=args.output)

    for i, podcast in enumerate(podcasts):
        print(f"Processing: {podcast['title']}")
        falas = generator.parse_dialogue(podcast['content'])
        if not falas:
            print(f"No dialogue found in {podcast['title']}, skipping.")
            continue

        segment_files = await generator.generate_audio_segments(falas, i)

        filename = sanitize_filename(podcast['title']) + ".mp3"
        generator.stitch_audio(segment_files, filename)

    # Cleanup temp dir
    if os.path.exists(generator.temp_dir):
        try:
            os.rmdir(generator.temp_dir)
        except OSError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
