import os
from faster_whisper import WhisperModel

# ============================================================
# CONFIGURAÇÕES
# ============================================================

# Pasta onde estão os áudios
pasta_downloads = os.listdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "downloads"
))

arquivo_audio = pasta_downloads[0] if pasta_downloads else None

arquivo_txt = "transcricao.txt"

# # ============================================================
# # VERIFICAÇÃO
# # ============================================================

# if not os.path.exists(arquivo_audio):
#     raise FileNotFoundError(
#         f"\nArquivo não encontrado:\n{arquivo_audio}\n"
#         f"\nColoque o arquivo de áudio dentro da pasta 'downloads'."
#     )

# print(f"Áudio encontrado: {arquivo_audio}")


# ============================================================
# MODELO WHISPER
# ============================================================

print("\nCarregando modelo Whisper...")
print("Modelo: medium")
print("Dispositivo: CPU")
print("Compute type: int8")

model = WhisperModel(
    "medium",
    device="cpu",
    compute_type="int8"
)


# ============================================================
# TRANSCRIÇÃO
# ============================================================

print("\nIniciando transcrição...\n")

segments, info = model.transcribe(
    arquivo_audio,
    language="pt",
    beam_size=5,
    vad_filter=True
)


# ============================================================
# SALVA SOMENTE O TEXTO
# ============================================================

with open(
    arquivo_txt,
    "w",
    encoding="utf-8"
) as arquivo:

    for segment in segments:
        texto = segment.text.strip()

        if texto:
            arquivo.write(texto + " ")


# ============================================================
# RESULTADO
# ============================================================

print("\n" + "=" * 60)
print("TRANSCRIÇÃO CONCLUÍDA")
print("=" * 60)

print(f"\nArquivo salvo em:")
print(arquivo_txt)
