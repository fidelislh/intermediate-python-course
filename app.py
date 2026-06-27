import streamlit as st
import asyncio
import os
import shutil
from podcast_generator import PodcastGenerator, split_dialogo_by_podcast, sanitize_filename, check_ffmpeg

st.set_page_config(page_title="Gerador de Podcast com IA", page_icon="🎙️")

st.title("🎙️ Gerador de Podcast com Duas Vozes")
st.markdown("""
Esta aplicação transforma seus diálogos em podcasts realistas com as vozes de **Joe** e **Jane**.
Insira seu texto abaixo ou faça o upload de um arquivo .txt.
""")

# Sidebar for configuration
st.sidebar.header("Configurações")
joe_voice = st.sidebar.selectbox("Voz do Joe", ["pt-BR-AntonioNeural", "pt-BR-ThalitaMultilingualNeural"])
jane_voice = st.sidebar.selectbox("Voz da Jane", ["pt-BR-FranciscaNeural", "pt-BR-ThalitaMultilingualNeural"])

# ffmpeg check
if not check_ffmpeg():
    st.error("ERRO: ffmpeg não encontrado no sistema. Por favor, instale o ffmpeg para continuar.")
    st.stop()

# Input section
tabs = st.tabs(["📝 Colar Texto", "📁 Upload de Arquivo"])

with tabs[0]:
    text_input = st.text_area("Cole seu diálogo aqui:", height=300, placeholder="Podcast 1 – Título\nJOE: Oi Jane!\nJANE: Oi Joe!")

with tabs[1]:
    uploaded_file = st.file_uploader("Escolha um arquivo .txt", type=["txt"])
    if uploaded_file is not None:
        text_input = uploaded_file.read().decode("utf-8")

if st.button("Gerar Podcast", type="primary"):
    if not text_input.strip():
        st.warning("Por favor, insira algum texto.")
    else:
        podcasts = split_dialogo_by_podcast(text_input)
        generator = PodcastGenerator(voice_joe=joe_voice, voice_jane=jane_voice, output_dir="web_output")

        for i, podcast in enumerate(podcasts):
            st.subheader(f"Processando: {podcast['title']}")
            falas = generator.parse_dialogue(podcast['content'])

            if not falas:
                st.write("Nenhum diálogo encontrado, pulando...")
                continue

            with st.spinner(f"Gerando áudio para {podcast['title']}..."):
                # Run async task in streamlit
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                segment_files = loop.run_until_complete(generator.generate_audio_segments(falas, i))

                filename = sanitize_filename(podcast['title']) + ".mp3"
                generator.stitch_audio(segment_files, filename)

                output_path = os.path.join("web_output", filename)

                if os.path.exists(output_path):
                    st.success(f"Pronto: {podcast['title']}")
                    with open(output_path, "rb") as f:
                        st.audio(f.read(), format="audio/mp3")
                        st.download_button(
                            label=f"Download {filename}",
                            data=f,
                            file_name=filename,
                            mime="audio/mp3",
                            key=f"dl_{i}"
                        )
                else:
                    st.error(f"Falha ao gerar {filename}")

# Cleanup (optional or periodic)
if st.sidebar.button("Limpar Arquivos Gerados"):
    if os.path.exists("web_output"):
        shutil.rmtree("web_output")
        st.success("Arquivos limpos!")
