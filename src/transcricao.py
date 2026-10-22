import os
from faster_whisper import WhisperModel

class TranscriptionService:
    def __init__(self):
        # Pasta onde estão os áudios
        self.pasta_downloads = os.listdir(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "audios"
        ))

        self.arquivo_audio = self.pasta_downloads[0] if self.pasta_downloads else None

        self.arquivo_txt = "transcricao.txt"

        # ============================================================
        # MODELO WHISPER
        # ============================================================

        print("\nCarregando modelo Whisper...")
        print("Modelo: medium")
        print("Dispositivo: CPU")
        print("Compute type: int8")

        self.model = WhisperModel(
            "medium",
            device="cpu",
            compute_type="int8"
        )

    def transcrever_audio(self):
        if not self.arquivo_audio:
            raise FileNotFoundError(
                "Nenhum arquivo de áudio encontrado na pasta 'downloads'."
            )

        # ============================================================
        # TRANSCRIÇÃO
        # ============================================================

        print("\nIniciando transcrição...\n")

        segments, info = self.model.transcribe(
            self.arquivo_audio,
            language="pt",
            beam_size=5,
            vad_filter=True
        )

        # ============================================================
        # SALVA SOMENTE O TEXTO
        # ============================================================

        with open(
            self.arquivo_txt,
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
        print(self.arquivo_txt)
