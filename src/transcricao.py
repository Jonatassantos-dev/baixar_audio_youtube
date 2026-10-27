from pathlib import Path

from faster_whisper import WhisperModel

class TranscriptionService:
    def __init__(self, arquivo_audio: Path | None = None):
        static_dir = Path(__file__).resolve().parent.parent / "static"
        pasta_audios = static_dir / "audios"
        pasta_audios.mkdir(parents=True, exist_ok=True)

        if arquivo_audio is None:
            arquivos_audio = sorted(
                caminho for caminho in pasta_audios.iterdir() if caminho.is_file()
            )
            arquivo_audio = arquivos_audio[0] if arquivos_audio else None

        self.arquivo_audio = Path(arquivo_audio) if arquivo_audio else None
        self.arquivo_txt = static_dir / "transcricao" / "transcricao.txt"

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
                "Nenhum arquivo de áudio foi informado ou encontrado em 'static/audios'."
            )

        # ============================================================
        # TRANSCRIÇÃO
        # ============================================================

        print("\nIniciando transcrição...\n")

        segments, info = self.model.transcribe(
            str(self.arquivo_audio),
            language="pt",
            beam_size=5,
            vad_filter=True
        )

        # ============================================================
        # SALVA SOMENTE O TEXTO
        # ============================================================

        self.arquivo_txt.parent.mkdir(parents=True, exist_ok=True)
        with self.arquivo_txt.open("w", encoding="utf-8") as arquivo:

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
