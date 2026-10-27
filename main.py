from pathlib import Path

from src.baixar_audio import BaixarAudioService
from src.extrair_transcricao_yt import YouTubeTranscriptService
from src.transcricao import TranscriptionService


STATIC_DIR = Path(__file__).resolve().parent / "static"


def transcricao_youtube(
    url: str, inicio: str, fim: str, idioma: tuple[str, ...] = ("pt", "pt-BR")
) -> bool:
    extrator = YouTubeTranscriptService()

    try:
        print(f"Obtendo transcrição do YouTube para o vídeo: {url}")
        trecho_transcrito = extrator.obter_trecho_youtube(
            url, inicio, fim, idioma=idioma
        )
        if not trecho_transcrito:
            raise ValueError("Não há transcrição disponível no intervalo informado.")
        print(f"Transcrição obtida com sucesso para o trecho {inicio} - {fim}.")
    except Exception as e:
        print(f"Erro ao obter transcrição do YouTube: {e}")
        return False

    try:
        print("Salvando transcrição em arquivo .docx...")
        extrator.salvar_docx(
            trecho_transcrito, STATIC_DIR / "transcricao" / "transcricao_youtube.docx"
        )
        print("Transcrição salva com sucesso em 'transcricao_youtube.docx'.")
    except Exception as e:
        print(f"Erro ao salvar transcrição em arquivo .docx: {e}")
        return False

    return True


def transcricao_manual(
    entrada_video: Path, tempo_inicio: str, tempo_fim: str, saida_audio: Path
) -> bool:
    service_audio = BaixarAudioService()

    try:
        print(
            f"Extraindo áudio do vídeo: {entrada_video} "
            f"(trecho {tempo_inicio} - {tempo_fim})"
        )
        audio_baixado = service_audio.extrair_audio(
            entrada_video, tempo_inicio, tempo_fim, saida_audio
        )
        print(f"Áudio extraído com sucesso: {audio_baixado}")
    except Exception as e:
        print(f"Erro ao extrair áudio: {e}")
        return False

    try:
        transcricao_service = TranscriptionService(audio_baixado)
        print("Transcrevendo áudio")
        transcricao_service.transcrever_audio()
        print("Transcrição concluída com sucesso. Arquivo 'transcricao.txt' gerado.")
    except Exception as e:
        print(f"Erro ao transcrever áudio: {e}")
        return False

    return True


def main():
    url = input("Digite a URL do vídeo do YouTube: ")
    inicio = input("Digite o tempo de início (formato HH:MM:SS ou MM:SS): ")
    fim = input("Digite o tempo de fim (formato HH:MM:SS ou MM:SS): ")

    if transcricao_youtube(url, inicio, fim):
        print("Transcrição do trecho do YouTube concluída com sucesso.")
    else:
        print("Falha na transcrição do trecho do YouTube.")
        print(
            "Coloque o vídeo em 'static/videos/culto.mp4' e tecle ENTER para "
            "continuar."
        )
        input()
        transcricao_manual(
            STATIC_DIR / "videos" / "culto.mp4",
            inicio,
            fim,
            STATIC_DIR / "audios" / "audio_extraido.mka",
        )

if __name__ == "__main__":
    main()