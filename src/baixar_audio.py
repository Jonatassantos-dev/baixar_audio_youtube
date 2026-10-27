import re
import subprocess
from pathlib import Path

class BaixarAudioService:
    def tempo_para_segundos(self, tempo: str) -> int:

        if not re.fullmatch(r"\d{1,}:\d{2}:\d{2}|\d{1,}:\d{2}", tempo):
            raise ValueError(
                f"Tempo inválido: {tempo}. "
                "Use HH:MM:SS ou MM:SS."
            )

        partes = [int(p) for p in tempo.split(":")]

        if len(partes) == 3:
            horas, minutos, segundos = partes
        else:
            horas = 0
            minutos, segundos = partes

        if segundos >= 60 or minutos >= 60 and len(partes) == 3:
            raise ValueError(f"Tempo inválido: {tempo}")

        return horas * 3600 + minutos * 60 + segundos

    def extrair_audio(
        self, entrada_video: Path, tempo_inicio: str, tempo_fim: str, saida_audio: Path
    ) -> Path:
        entrada_video = Path(entrada_video)
        saida_audio = Path(saida_audio)

        # Verifica se o FFmpeg está instalado
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError(
                "FFmpeg não encontrado. Instale-o e adicione-o ao PATH."
            )

        # Verifica se o vídeo existe
        if not entrada_video.is_file():
            raise FileNotFoundError(
                f"Vídeo não encontrado: {entrada_video.resolve()}"
            )

        # Valida o intervalo
        inicio = self.tempo_para_segundos(tempo_inicio)
        fim = self.tempo_para_segundos(tempo_fim)

        if fim <= inicio:
            raise ValueError(
                "O tempo final deve ser maior que o inicial."
            )

        # Cria a pasta de saída
        saida_audio.parent.mkdir(parents=True, exist_ok=True)

        # Extrai somente o áudio, sem recodificar
        comando = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-ss", tempo_inicio,
            "-i", str(entrada_video),
            "-t", str(fim - inicio),
            "-map", "0:a:0",
            "-vn",
            "-c:a", "copy",
            str(saida_audio.resolve())
        ]

        print(f"Vídeo: {entrada_video}")
        print(f"Início: {tempo_inicio}")
        print(f"Fim: {tempo_fim}")
        print(f"Duração solicitada: {fim - inicio} segundos")
        print("Extraindo áudio...")

        try:
            subprocess.run(comando, check=True)
        except subprocess.CalledProcessError as erro:
            raise RuntimeError(
                "Falha na extração. Verifique o vídeo, "
                "a faixa de áudio e o formato de saída."
            ) from erro

        print("\nExtração concluída!")
        print(f"Arquivo salvo em: {saida_audio.resolve()}")
        return saida_audio.resolve()
