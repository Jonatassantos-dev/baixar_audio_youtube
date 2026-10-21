import re
from urllib.parse import parse_qs, urlparse
from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeTranscriptService:

    def __init__(self, languages: tuple[str, ...] = ("pt", "pt-BR")):
        self.languages = languages
        self.api = YouTubeTranscriptApi()

    def extrair_video_id(self, url: str) -> str:

        if "youtu.be/" in url:
            return url.split("/")[-1].split("?")[0]

        parsed = urlparse(url)

        return parse_qs(parsed.query)["v"][0]

    def tempo_para_segundos(self, tempo: str) -> int:

        partes = tempo.split(":")

        if len(partes) not in (2, 3):
            raise ValueError("Formato inválido, use mm:ss ou hh:mm:ss")

        if len(partes) == 2:

            minutos, segundos = partes

            return int(minutos) * 60 + int(segundos)

        if len(partes) == 3:

            horas, minutos, segundos = partes

            return (
                int(horas) * 3600
                + int(minutos) * 60
                + int(segundos)
            )


    def obter_trecho_youtube(self, url: str, inicio: str, fim: str, idioma=("pt", "pt-BR")) -> str:

        video_id = self.extrair_video_id(url)

        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id,
            languages=list(idioma)
        )

        inicio_seg = self.tempo_para_segundos(inicio)

        fim_seg = self.tempo_para_segundos(fim)

        texto = []

        for trecho in transcript:

            if inicio_seg <= trecho.start <= fim_seg:

                texto.append(trecho.text.strip())

        return "\n".join(texto)

    def salvar_docx(self, texto, nome):
        doc = Document()

        texto_final = re.sub(r"\s+", " ", texto)

        texto_final = re.sub(r"\s+([.,!?;:])", r"\1", texto_final)

        texto_final = texto_final.strip()

        for linha in texto_final.split("\n"):

            linha = linha.strip()

            if linha:

                doc.add_paragraph(linha)

        doc.save(nome)