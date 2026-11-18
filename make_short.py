import json
import os
import textwrap

from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920  # vertical 9:16
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CORES = ["#1e3a8a", "#7c2d12", "#14532d", "#581c87"]
PASTA_TMP = "tmp"
PASTA_SAIDA = "saida"


def criar_slide(texto, cor, caminho):
    img = Image.new("RGB", (W, H), cor)
    draw = ImageDraw.Draw(img)
    fonte = ImageFont.truetype(FONT, 80)
    linhas = textwrap.wrap(texto, width=20)
    altura_linha = 110
    y = (H - altura_linha * len(linhas)) // 2
    for linha in linhas:
        largura = draw.textlength(linha, font=fonte)
        draw.text(((W - largura) / 2, y), linha, font=fonte, fill="white")
        y += altura_linha
    img.save(caminho)


def main():
    os.makedirs(PASTA_TMP, exist_ok=True)
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    with open("roteiro.json", encoding="utf-8") as f:
        roteiro = json.load(f)

    clips = []
    for i, slide in enumerate(roteiro["slides"]):
        png = f"{PASTA_TMP}/slide{i}.png"
        mp3 = f"{PASTA_TMP}/fala{i}.mp3"

        criar_slide(slide["texto"], CORES[i % len(CORES)], png)
        gTTS(slide["fala"], lang=roteiro.get("lang", "pt")).save(mp3)

        audio = AudioFileClip(mp3)
        clip = (
            ImageClip(png)
            .set_duration(audio.duration + 0.4)
            .set_audio(audio)
        )
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        f"{PASTA_SAIDA}/short.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
    )


if __name__ == "__main__":
    main()
