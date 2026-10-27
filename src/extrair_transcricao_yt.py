import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeTranscriptService:

    def __init__(self, languages: tuple[str, ...] = ("pt", "pt-BR")):
        self.languages = languages
        self.api = YouTubeTranscriptApi()

    def extrair_video_id(self, url: str) -> str:
        parsed = urlparse(url)
        host = parsed.netloc.lower()

        if host == "youtu.be":
            video_id = parsed.path.strip("/").split("/")[0]
        elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            if parsed.path == "/watch":
                video_id = parse_qs(parsed.query).get("v", [""])[0]
            elif parsed.path.startswith(("/shorts/", "/embed/")):
                video_id = parsed.path.split("/")[2]
            else:
                video_id = ""
        else:
            video_id = ""

        if not video_id:
            raise ValueError("URL do YouTube inválida ou sem identificador de vídeo.")
        return video_id

    def tempo_para_segundos(self, tempo: str) -> int:
        if not re.fullmatch(r"\d+:\d{2}:\d{2}|\d+:\d{2}", tempo):
            raise ValueError("Formato inválido, use mm:ss ou hh:mm:ss")

        partes = [int(parte) for parte in tempo.split(":")]
        if partes[-1] >= 60 or (len(partes) == 3 and partes[-2] >= 60):
            raise ValueError(f"Tempo inválido: {tempo}")

        if len(partes) == 2:
            minutos, segundos = partes
            return minutos * 60 + segundos

        horas, minutos, segundos = partes
        return horas * 3600 + minutos * 60 + segundos

    def obter_trecho_youtube(
        self,
        url: str,
        inicio: str,
        fim: str,
        idioma: tuple[str, ...] | None = None,
    ) -> str:
        video_id = self.extrair_video_id(url)
        inicio_seg = self.tempo_para_segundos(inicio)
        fim_seg = self.tempo_para_segundos(fim)
        if fim_seg <= inicio_seg:
            raise ValueError("O tempo final deve ser maior que o inicial.")

        idiomas = idioma if idioma is not None else self.languages
        transcript = self.api.fetch(video_id, languages=list(idiomas))

        texto = []

        for trecho in transcript:

            if inicio_seg <= trecho.start <= fim_seg:

                texto.append(trecho.text.strip())

        return "\n".join(texto)

    def salvar_docx(self, texto: str, nome: str | Path) -> None:
        doc = Document()

        texto_final = re.sub(r"\s+", " ", texto)

        texto_final = re.sub(r"\s+([.,!?;:])", r"\1", texto_final)

        texto_final = texto_final.strip()

        for linha in texto_final.split("\n"):

            linha = linha.strip()

            if linha:

                doc.add_paragraph(linha)

        caminho = Path(nome)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        doc.save(caminho)