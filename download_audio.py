import os
import re
import subprocess
from pathlib import Path

from pytubefix import YouTube
from pytubefix.cli import on_progress


# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL = "https://www.youtube.com/watch?v=Cl9vD_g7G_w&t=6166s"

# Informe None para baixar o áudio completo
INICIO = "36:44"
FIM = "1:27:00"

PASTA_DOWNLOAD = Path("downloads")


# ============================================================
# FUNÇÕES
# ============================================================

def tempo_para_segundos(tempo):

    if tempo is None:
        return None

    tempo = str(tempo).strip()

    partes = tempo.split(":")

    try:
        partes = [int(x) for x in partes]
    except ValueError:
        raise ValueError(
            f"Tempo inválido: {tempo}. "
            "Use formatos como 45, 01:30 ou 01:44:34."
        )

    if len(partes) == 1:
        # SS
        return partes[0]

    elif len(partes) == 2:
        # MM:SS
        minutos, segundos = partes
        return minutos * 60 + segundos

    elif len(partes) == 3:
        # HH:MM:SS
        horas, minutos, segundos = partes
        return horas * 3600 + minutos * 60 + segundos

    else:
        raise ValueError(f"Formato de tempo inválido: {tempo}")


def segundos_para_ffmpeg(segundos):
    """
    Converte segundos para HH:MM:SS.
    """

    segundos = int(segundos)

    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos = segundos % 60

    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def limpar_nome(nome):
    """
    Remove caracteres inválidos para nomes de arquivos no Windows.
    """

    nome = re.sub(r'[<>:"/\\|?*]', '', nome)
    nome = re.sub(r'\s+', ' ', nome)

    return nome.strip()


def verificar_ffmpeg():
    """
    Verifica se o FFmpeg está instalado.
    """

    try:
        resultado = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if resultado.returncode != 0:
            raise Exception

    except Exception:
        print("\nERRO: FFmpeg não encontrado.")
        print("\nInstale o FFmpeg e adicione-o ao PATH.")
        print("Depois teste com:")
        print("\n    ffmpeg -version\n")

        raise SystemExit(1)


def cortar_audio(arquivo_entrada, arquivo_saida, inicio, fim=None):
    """
    Usa FFmpeg para converter/cortar o áudio.
    """

    inicio_segundos = tempo_para_segundos(inicio)

    if inicio_segundos is None:
        inicio_segundos = 0

    inicio_ffmpeg = segundos_para_ffmpeg(inicio_segundos)

    comando = [
        "ffmpeg",
        "-y",
        "-ss",
        inicio_ffmpeg,
        "-i",
        str(arquivo_entrada),
    ]

    if fim is not None:
        fim_segundos = tempo_para_segundos(fim)

        if fim_segundos <= inicio_segundos:
            raise ValueError(
                "O fim precisa ser maior que o início."
            )

        duracao = fim_segundos - inicio_segundos

        comando.extend([
            "-t",
            segundos_para_ffmpeg(duracao)
        ])

    # Converte para MP3
    comando.extend([
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(arquivo_saida)
    ])

    print("\nConvertendo/cortando com FFmpeg...")
    print("Comando:")
    print(" ".join(f'"{x}"' if " " in str(x) else str(x)
                  for x in comando))

    resultado = subprocess.run(comando)

    if resultado.returncode != 0:
        raise RuntimeError(
            "O FFmpeg encontrou um erro ao processar o áudio."
        )


# ============================================================
# DOWNLOAD
# ============================================================

def main():

    verificar_ffmpeg()

    PASTA_DOWNLOAD.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 60)
    print(" YOUTUBE AUDIO DOWNLOADER")
    print("=" * 60)

    print("\nObtendo informações do vídeo...")

    try:

        yt = YouTube(
            URL,
            on_progress_callback=on_progress
        )

        print(f"\nTítulo:")
        print(yt.title)

        print(f"\nCanal:")
        print(yt.author)

        print(f"\nDuração:")
        print(yt.length, "segundos")

    except Exception as e:

        print("\nErro ao acessar o vídeo:")
        print(e)

        return

    # ========================================================
    # STREAM DE ÁUDIO
    # ========================================================

    print("\nProcurando stream de áudio...")

    try:

        # Prefere MP4/M4A
        audio = yt.streams.get_audio_only(subtype="mp4")

        if audio is None:
            print("MP4 não encontrado. Tentando qualquer áudio...")
            audio = yt.streams.get_audio_only()

        if audio is None:
            raise Exception(
                "Nenhum stream de áudio disponível."
            )

        print("\nStream encontrado:")
        print(f"Mime type : {audio.mime_type}")
        print(f"Codec     : {audio.audio_codec}")
        print(f"Bitrate   : {audio.abr}")
        print(f"Itag      : {audio.itag}")

    except Exception as e:

        print("\nErro ao encontrar áudio:")
        print(e)

        return

    # ========================================================
    # NOME DOS ARQUIVOS
    # ========================================================

    titulo = limpar_nome(yt.title)

    arquivo_temporario = (
        PASTA_DOWNLOAD / f"{titulo}_original.mp4"
    )

    arquivo_final = (
        PASTA_DOWNLOAD / f"{titulo}.mp3"
    )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    print("\nIniciando download...")

    try:

        arquivo_baixado = audio.download(
            output_path=str(PASTA_DOWNLOAD),
            filename=arquivo_temporario.name,
            skip_existing=False
        )

        print("\nDownload concluído:")
        print(arquivo_baixado)

    except Exception as e:

        print("\nErro durante o download:")
        print(e)

        return

    # ========================================================
    # CORTE / CONVERSÃO
    # ========================================================

    try:

        cortar_audio(
            arquivo_entrada=arquivo_baixado,
            arquivo_saida=arquivo_final,
            inicio=INICIO,
            fim=FIM
        )

    except Exception as e:

        print("\nErro ao processar áudio:")
        print(e)

        return

    # ========================================================
    # REMOVE TEMPORÁRIO
    # ========================================================

    try:

        os.remove(arquivo_baixado)

    except Exception:
        pass

    # ========================================================
    # RESULTADO
    # ========================================================

    print("\n" + "=" * 60)
    print(" DOWNLOAD FINALIZADO")
    print("=" * 60)

    print(f"\nArquivo:")
    print(arquivo_final)

    if INICIO or FIM:

        print("\nTrecho:")
        print(f"Início: {INICIO}")
        print(f"Fim:    {FIM}")

    print("\nFormato: MP3")
    print("Bitrate: 192 kbps")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()