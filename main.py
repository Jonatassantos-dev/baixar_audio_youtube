from src.baixar_audio import *
from src.extrair_transcricao_yt import *
from src.transcricao import *

def transcricao_youtube(url: str, inicio: str, fim: str, idioma=("pt", "pt-BR")) -> str:
    
    extrator = YouTubeTranscriptService()

    try:
        print(f"Obtendo transcrição do YouTube para o vídeo: {url}")
        trecho_transcrito = extrator.obter_trecho_youtube(url, inicio, fim, idioma="pt")
        print(f"Trancrição obtida com sucesso para o trecho {inicio} - {fim}.")
    except Exception as e:
        print(f"Erro ao obter transcrição do YouTube: {e}")
        return False

    try:
        print("Salvando transcrição em arquivo .docx...")
        extrator.salvar_docx(trecho_transcrito, "transcricao_youtube")
        print("Transcrição salva com sucesso em 'transcricao_youtube.docx'.")
    except Exception as e:
        print(f"Erro ao salvar transcrição em arquivo .docx: {e}")
        return False

    return True

def transcricao_manual(entrada_video: str, tempo_inicio: str, tempo_fim: str, saida_audio: str) -> None:

    service_audio = BaixarAudioService()

    try:
        print(f"Extraindo áudio do vídeo: {entrada_video} (trecho {tempo_inicio} - {tempo_fim})")
        audio_baixado = service_audio.extrair_audio(entrada_video, tempo_inicio, tempo_fim, saida_audio)
        print(f"Áudio extraído com sucesso: {audio_baixado}")
    except Exception as e:
        print(f"Erro ao extrair áudio: {e}")
        return

    if audio_baixado:
        transcricao_service = TranscriptionService()
        print("Transcrevendo áudio")
        try:
            transcricao_service.transcrever_audio()
            print("Transcrição concluída com sucesso. Arquivo 'transcricao.txt' gerado.")
        except Exception as e:
            print(f"Erro ao transcrever áudio: {e}")


def main():
    url = input("Digite a URL do vídeo do YouTube: ")
    inicio = input("Digite o tempo de início (formato HH:MM:SS ou MM:SS): ")
    fim = input("Digite o tempo de fim (formato HH:MM:SS ou MM:SS): ")

    if transcricao_youtube(url, inicio, fim):
        print("Transcrição do trecho do YouTube concluída com sucesso.")
    else:
        print("Falha na transcrição do trecho do YouTube.")
        print("Baixe o video no site turboscribe ai download youtube e coloque na pasta 'videos', e depois tecle ENTER para continuar.")
        input()
        transcricao_manual("culto.mp4", inicio, fim, "audio_extraido.mka")

if __name__ == '__main__':
    main()