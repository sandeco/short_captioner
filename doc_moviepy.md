# importação
from moviepy import VideoFileClip, CompositeVideoClip, TextClip

# Olha como se dá as importações dentro de moviepy

"""Importa tudo que você precisa dos submódulos do MoviePy para que tudo
possa ser importado diretamente com ``from moviepy import *``.
"""

from moviepy.audio import fx as afx
from moviepy.audio.AudioClip import (
    AudioArrayClip,
    AudioClip,
    CompositeAudioClip,
    concatenate_audioclips,
)
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.Effect import Effect
from moviepy.tools import convert_to_seconds
from moviepy.version import __version__
from moviepy.video import fx as vfx, tools as videotools
from moviepy.video.compositing.CompositeVideoClip import (
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
)
from moviepy.video.io import ffmpeg_tools
from moviepy.video.io.display_in_notebook import display_in_notebook
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import (
    BitmapClip,
    ColorClip,
    DataVideoClip,
    ImageClip,
    TextClip,
    UpdatedVideoClip,
    VideoClip,
)


# Add display in notebook to video and audioclip
VideoClip.display_in_notebook = display_in_notebook
AudioClip.display_in_notebook = display_in_notebook


# Importing with `from moviepy import *` will only import these names
__all__ = [
    "__version__",
    "VideoClip",
    "DataVideoClip",
    "UpdatedVideoClip",
    "ImageClip",
    "ColorClip",
    "TextClip",
    "BitmapClip",
    "VideoFileClip",
    "CompositeVideoClip",
    "clips_array",
    "ImageSequenceClip",
    "concatenate_videoclips",
    "AudioClip",
    "AudioArrayClip",
    "CompositeAudioClip",
    "concatenate_audioclips",
    "AudioFileClip",
    "Effect",
    "vfx",
    "afx",
    "videotools",
    "ffmpeg_tools",
    "convert_to_seconds",
]



# Documentação da classe TextClip

A classe `TextClip` é usada para criar clipes de vídeo a partir de texto gerado por script, servindo como uma subclasse de `ImageClip`.

## Parâmetros da classe TextClip

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `font` | `str` | Caminho para a fonte (formato OpenType) a ser usada. Se `None`, usa a fonte padrão do Pillow. |
| `text` | `str` | O texto a ser escrito no clipe. Alternativa ao parâmetro `filename`. |
| `filename` | `str` ou `path-like` | O nome de um arquivo contendo o texto a ser escrito. Alternativa ao parâmetro `text`. |
| `font_size` | `int` | Tamanho da fonte em pontos. Pode ser definido automaticamente se o método for 'caption' ou 'label' com tamanho fixo. |
| `size` | `tuple` | Tamanho da imagem em pixels (largura, altura). Obrigatório para o método 'caption' e pode ser usado para 'label'. |
| `margin` | `tuple` | Margem em pixels ao redor do texto, como `(horizontal, vertical)` ou `(left, top, right, bottom)`. |
| `color` | `tuple` ou `str` | Cor do texto. Padrão é "black". Aceita tupla RGB/RGBA, nome de cor ou notação hexadecimal. |
| `bg_color` | `tuple` ou `str` | Cor de fundo. Padrão é `None` (sem fundo). Aceita tupla RGB/RGBA, nome de cor ou notação hexadecimal. |
| `stroke_color` | `tuple` ou `str` | Cor do contorno do texto. `None` por padrão. |
| `stroke_width` | `int` | Largura do contorno em pixels. |
| `method` | `str` | "label" (padrão) para dimensionamento automático do clipe para ajustar o texto, ou "caption" para quebra de texto em um tamanho fixo. |
| `text_align` | `str` | Alinhamento horizontal do texto (`center`, `left`, `right`). Padrão é `left`. |
| `horizontal_align` | `str` | Alinhamento horizontal do bloco de texto na imagem (`center`, `left`, `right`). Padrão é `center`. |
| `vertical_align` | `str` | Alinhamento vertical do bloco de texto na imagem (`center`, `top`, `bottom`). Padrão é `center`. |
| `interline` | `int` | Espaçamento entre as linhas. Padrão é `4`. |
| `transparent` | `bool` | Se `True`, a transparência na imagem é considerada. Padrão é `True`. |
| `duration` | `number` | Duração do clipe em segundos. |

---

## Métodos da classe TextClip

`TextClip` não possui métodos próprios além do construtor. Ele herda todos os métodos de suas classes pai, `ImageClip`, `VideoClip` e `Clip`.

### Métodos herdados da classe ImageClip

| Método | Descrição |
| :--- | :--- |
| `transform` | Aplica um filtro de transformação geral. O clipe resultante é da classe `VideoClip`. |
| `image_transform` | Aplica um filtro de transformação de imagem, calculando o resultado uma única vez. |
| `time_transform` | Aplica uma transformação na linha do tempo. Não tem efeito na imagem estática, mas pode afetar a máscara ou o áudio. |

### Métodos herdados da classe VideoClip

| Método | Descrição |
| :--- | :--- |
| `save_frame(filename, t, with_mask)` | Salva um quadro do clipe como um arquivo de imagem em um tempo `t` específico. |
| `write_videofile(filename, ...)` | Escreve o clipe em um arquivo de vídeo. |
| `write_images_sequence(name_format, ...)` | Escreve o clipe como uma sequência de arquivos de imagem. |
| `write_gif(filename, ...)` | Converte e salva o clipe como um arquivo GIF animado. |
| `show(t, with_mask)` | Exibe um quadro do clipe em uma janela. |
| `preview(fps, audio, ...)` | Exibe o clipe em uma janela, permitindo a reprodução em tempo real com ou sem áudio. |
| `with_effects_on_subclip(effects, start_time, end_time, ...)` | Aplica uma lista de efeitos em um sub-clipe. |
| `image_transform(image_func, ...)` | Modifica os quadros do clipe aplicando uma função a cada quadro. |
| `fill_array(pre_array, shape)` | Preenche um array para corresponder a um formato específico. |
| `compose_on(background, t)` | Compõe o quadro do clipe sobre uma imagem de fundo no tempo `t`. |
| `compose_mask(background_mask, t)` | Compõe a máscara do clipe sobre uma máscara de fundo. |
| `with_background_color(size, color, pos, opacity)` | Coloca o clipe sobre um fundo colorido. |
| `with_updated_frame_function(frame_function)` | Retorna uma cópia do clipe com uma nova função de quadro. |
| `with_audio(audioclip)` | Anexa um clipe de áudio ao clipe de vídeo. |
| `with_mask(mask)` | Define a máscara do clipe. |
| `without_mask()` | Remove a máscara do clipe. |
| `with_opacity(opacity)` | Define o nível de opacidade do clipe. |
| `with_position(pos, relative)` | Define a posição do clipe em composições. |
| `with_layer_index(index)` | Define a camada do clipe em composições. |
| `resized(new_size, height, width, apply_to_mask)` | Retorna uma versão redimensionada do clipe. |
| `rotated(angle, ...)` | Retorna uma versão rotacionada do clipe. |
| `cropped(x1, y1, ...)` | Retorna um novo clipe com uma sub-região retangular do clipe original. |
| `to_ImageClip(t, with_mask, duration)` | Retorna um `ImageClip` a partir de um quadro do clipe em um tempo `t` específico. |
| `to_mask(canal)` | Converte o clipe em um clipe de máscara. |
| `to_RGB()` | Converte um clipe de máscara em um clipe RGB. |
| `without_audio()` | Remove o áudio do clipe. |
| `__add__(other)` | Concatena dois clipes de vídeo. |
| `__or__(other)` | Cria um clipe com dois clipes lado a lado. |
| `__truediv__(other)` | Cria um clipe com um clipe em cima do outro. |
| `__matmul__(n)` | Rotaciona o clipe por `n` graus. |
| `__and__(mask)` | Usa outro clipe como máscara. |

### Métodos herdados da classe Clip

| Método | Descrição |
| :--- | :--- |
| `with_start(start)` | Retorna uma cópia do clipe com um novo tempo de início. |
| `with_duration(duration)` | Retorna uma cópia do clipe com uma nova duração. |
| `with_end(end)` | Retorna uma cópia do clipe com um novo tempo de fim. |
| `subclipped(t_start, t_end)` | Retorna um sub-clipe entre os tempos `t_start` e `t_end`. |
| `with_is_playing(t_start, t_end)` | Retorna um clipe que tem uma função que retorna verdadeiro entre `t_start` e `t_end`. |
| `with_end_after(other)` | Altera a duração do clipe para que ele termine após o clipe `other`. |
| `with_start_at_end_of(other)` | Altera o tempo de início do clipe para que ele comece no final do clipe `other`. |
| `with_start_at(start)` | Define o tempo de início do clipe. |
| `fx(function, *args, **kwargs)` | Aplica um filtro de função ao clipe. |
| `with_effects(effects, **kwargs)` | Aplica uma lista de efeitos ao clipe. |
| `with_time_transform(func, keep_duration, apply_to)` | Aplica uma transformação de tempo ao clipe. |
| `with_speedx(factor, final_duration, change_end, apply_to)` | Muda a velocidade do clipe. |
| `with_time_offset(offset, apply_to)` | Adiciona um deslocamento de tempo ao clipe. |
| `with_loop(nloops, duration)` | Faz o clipe ser executado em loop. |
| `with_transfx(transfx)` | Aplica uma transformação de tempo ao clipe. |
| `with_on_color(size, color, pos)` | Coloca o clipe sobre um fundo colorido. |
| `with_set_is_mask(is_mask)` | Define se o clipe é uma máscara. |
| `get_frame(t)` | Retorna um quadro do clipe no tempo `t`. |
| `with_iter_frames(fps, with_times, progress_bar, with_mask, logger)` | Itera sobre os quadros do clipe. |
| `with_make_frame(t)` | Retorna um quadro no tempo `t`. |
| `preview(fps, audio)` | Exibe o clipe em uma janela. |
| `close()` | Fecha o clipe. |


Ok, aqui está a versão reduzida e direta para a regra.

-----

### Regra para IA: `subclip` agora é `subclipped` em MoviePy

**O que detectar:** O uso do método `.subclip()` em qualquer objeto da biblioteca MoviePy.

**O que fazer:** Substituir automaticamente `.subclip()` por `.subclipped()`.

**Exemplo:**

  * **NÃO FAÇA:**

    ```python
    # Código antigo/incorreto
    clipe_cortado = video.subclip(10, 20)
    ```

  * **FAÇA:**

    ```python
    # Código novo/correto
    clipe_cortado = video.subclipped(10, 20)
    ```


# DOCUMENTAÇÃO DA CLASSE TextClip

A classe `TextClip` é usada para criar clipes de texto em vídeos.

## vamos listar:
- parâmetros
- métodos
- metodos herdados

# Documentação de `TextClip` (MoviePy)  
*Linha de herança:* `TextClip` → `ImageClip` → `VideoClip` → `Clip`  
> **Escopo:** abaixo estão **todos os parâmetros públicos** do construtor de `TextClip` e **os métodos públicos utilizáveis** herdados ao longo da cadeia de herança **com base exclusivamente no código fornecido**. A classe-base `Clip` não está no trecho; portanto, métodos definidos somente em `Clip` não são listados aqui.

---

## Visão geral

`TextClip` gera um **quadro estático** (imagem) com texto renderizado via **Pillow** e o expõe como um **videoclipe estático** (um frame repetido pela duração informada).  
Ele é ideal para **legendas**, **cards**, **títulos** e **faixas** sobrepostas em composições.

- **Tipo:** clip de imagem **estática** (não animado por si só, mas pode receber transformações e composições).  
- **Transparência:** suporta fundo transparente e **canal alfa** (quando `transparent=True` e/ou `bg_color` RGBA).  
- **Máscara:** quando transparente, o canal alfa é tratado como **máscara** do clip.

---

## Construtor

```python
TextClip(
    font=None,
    text=None,
    filename=None,
    font_size=None,
    size=(None, None),
    margin=(None, None),
    color="black",
    bg_color=None,
    stroke_color=None,
    stroke_width=0,
    method="label",
    text_align="left",
    horizontal_align="center",
    vertical_align="center",
    interline=4,
    transparent=True,
    duration=None,
)


Parâmetros (públicos)
Parâmetro	Tipo	Default	Descrição / Comportamento
font	str (path para fonte .otf/.ttf)	None	Fonte TrueType/OpenType usada pela Pillow. Se None, usa a fonte padrão da Pillow. Erros de abertura levantam ValueError.
text	str	None	Texto a renderizar. Obrigatório se filename não for usado.
filename	str/path	None	Carrega o texto de um arquivo. Se fornecido, substitui text. Decorado para aceitar path-like.
font_size	int	None	Tamanho da fonte em pontos. Pode ser autoajustado dependendo do method e de size.
size	(width, height) com int ou None	(None, None)	Tamanho da imagem final (largura, altura). Dependências variam conforme method. Para caption, width é obrigatório; height pode ser None se font_size for definido.
margin	(horiz, vert) ou (left, top, right, bottom)	(None, None)	Margens em pixels adicionadas ao redor do texto. Aceita forma simétrica (2 valores) ou assimétrica (4 valores).
color	tuple/str	"black"	Cor do texto (RGB ou nome/hex; em RGBA se transparent=True).
bg_color	tuple/str/None	None	Cor de fundo do quadro. None com transparent=True implica fundo totalmente transparente (0,0,0,0).
stroke_color	tuple/str/None	None	Cor do contorno do texto (traçado). None desativa o contorno.
stroke_width	int	0	Largura do traçado em pixels (>= 0).
method	"label" | "caption"	"label"	label: imagem se ajusta ao texto (auto-calcula font_size se width for dado, ou width/height se font_size for dado). caption: texto quebra em uma imagem de tamanho fixo (size), com quebra de linha/ajuste de fonte conforme necessário.
text_align	"left" | "center" | "right"	"left"	Alinhamento do texto dentro do bloco (similar ao CSS).
horizontal_align	"left" | "center" | "right"	"center"	Alinhamento horizontal do bloco de texto dentro da imagem final (considera margens).
vertical_align	"top" | "center" | "bottom"	"center"	Alinhamento vertical do bloco de texto dentro da imagem final (considera margens).
interline	int	4	Espaçamento entre linhas (pontos/pixels coerentes com Pillow).
transparent	bool	True	Se True, cria imagem em RGBA; se bg_color=None, fundo fica transparente.
duration	float/int/None	None	Duração do clip (segundos). Se None, o clip terá duração indefinida até ser usado em composições ou recortes.

Validações e notas importantes

Fonte: se font não puder ser carregada por ImageFont.truetype, um ValueError é lançado.

Texto: é obrigatório (direto via text ou indiretamente via filename).

Method: deve ser "label" ou "caption"; caso contrário, lança ValueError.

caption:

width (componente size[0]) é obrigatório.

Se height (size[1]) for None, exige font_size (e a altura será computada).

Caso font_size seja None, será otimizado automaticamente para caber no retângulo width × height.

O texto é quebrado automaticamente em múltiplas linhas para não exceder width.

label:

Se font_size for None e img_width (size[0]) também for None, lança ValueError (uma das duas dimensões deve guiar o ajuste).

Se o img_width for None, ele é derivado do conteúdo (text) usando font_size.

img_height é derivado do texto e espaçamento quando não especificado.

Métrica de altura real: a implementação considera ascent e descent da fonte (baseline) para estimar altura real do bloco textual, evitando cortes em caracteres com acentos/caudas.

Atributos relevantes em TextClip

Além dos atributos herdados (ver seções abaixo), TextClip define/propaga:

text: conteúdo textual efetivo (após leitura de arquivo, se filename foi usado).

color, stroke_color: cores finais aplicadas.

img: numpy.ndarray com o frame em RGB(A) gerado pela Pillow.

size: (w, h) da imagem final.

mask: se transparent=True com bg_color RGBA ou fundo transparente, o alfa é tratado como máscara.

duration: duração (se fornecida).

is_mask (herdado): sempre False para TextClip regular (clip de imagem, não de máscara).

Métodos públicos utilizáveis por TextClip

Observação: TextClip não adiciona métodos públicos próprios além do construtor; os métodos utilizáveis vêm de ImageClip e VideoClip.
Métodos “dunder” (__add__, etc.) também são listados por serem operadores públicos úteis.

Métodos herdados de ImageClip (pai direto)

ImageClip especializa um VideoClip para quadros estáticos. Alguns métodos retornam um VideoClip (deixa de ser “estático” após certas transformações).

transform(func, apply_to=None, keep_duration=True)
Transformação geral no conteúdo de imagem, potencialmente tornando-o animado. Retorna um VideoClip.

image_transform(image_func, apply_to=None) (decorado com @outplace)
Aplica image_func(frame) uma única vez (como clip estático) e atualiza img/size. Pode propagar para mask/audio se listados em apply_to.

time_transform(time_func, apply_to=None, keep_duration=False) (decorado com @outplace)
Transforma a linha do tempo (não altera o frame estático, mas pode afetar mask/audio).

Métodos herdados de VideoClip (avô)
Exportação / IO

save_frame(filename, t=0, with_mask=True)
Salva quadro (PNG suporta alfa quando with_mask=True).

write_videofile(filename, fps=None, codec=None, bitrate=None, audio=True, audio_fps=44100, preset="medium", audio_nbytes=4, audio_codec=None, audio_bitrate=None, audio_bufsize=2000, temp_audiofile=None, temp_audiofile_path="", remove_temp=True, write_logfile=False, threads=None, ffmpeg_params=None, logger="bar", pixel_format=None)
Renderiza para arquivo de vídeo via FFmpeg. Integra áudio se houver self.audio.

write_images_sequence(name_format, fps=None, with_mask=True, logger="bar")
Exporta sequência de imagens.

write_gif(filename, fps=None, loop=0, logger="bar")
Exporta GIF animado (via imageio).

Visualização / Preview

show(t=0, with_mask=True)
Abre o quadro (Pillow viewer) para inspeção rápida.

preview(fps=15, audio=True, audio_fps=22050, audio_buffersize=3000, audio_nbytes=2)
Toca o clip (vídeo/áudio) em janela de preview (ffplay).

Efeitos / Edição temporal

with_effects_on_subclip(effects, start_time=0, end_time=None, **kwargs)
Aplica lista de efeitos apenas no subtrecho [start_time, end_time) e reconcatena.

image_transform(image_func, apply_to=None)
Versão genérica no nível VideoClip (frame-a-frame, caso animado).

Composição (blending / overlay)

fill_array(pre_array, shape=(0, 0))
Utilitário para ajustar array ao shape desejado.

compose_on(background: PIL.Image, t)
Composita frame do clip sobre background (leva em conta alfa/máscara).

compose_mask(background_mask: np.ndarray, t)
Composita máscara deste clip sobre background_mask (opera em escala [0..1], acumulando opacidades corretamente).

with_background_color(size=None, color=(0,0,0), pos=None, opacity=None)
Coloca o clip sobre fundo colorido; útil para flatten de transparência. Pode retornar ImageClip quando aplicável.

Ajustes do clip (atributos/máscara/áudio)

with_updated_frame_function(frame_function) (decorado com @outplace)
Substitui a função de frame e recalcula size.

with_audio(audioclip) (outplace)
Anexa um AudioClip ao vídeo.

with_mask(mask="auto") (outplace, add_mask_if_none)
Define a máscara do clip. Com "auto": gera máscara sólida de 1.0 se tamanho constante; caso contrário, máscara dinâmica.

without_mask() (outplace)
Remove a máscara.

with_opacity(opacity) (outplace, add_mask_if_none)
Ajusta opacidade multiplicando a máscara por opacity (0..1).

with_position(pos, relative=False) (outplace, apply_to_mask)
Define posição para composições. Aceita (x,y), palavras-chave ("center", "top", etc.) ou função t→(x,y). relative=True permite valores relativos (ex.: (0.4, 0.7)).

with_layer_index(index) (outplace, apply_to_mask)
Define ordem de empilhamento em composições (índice maior sobrepõe).

without_audio() (outplace)
Remove o áudio.

Geometria (atalhos que encapsulam efeitos)

resized(new_size=None, height=None, width=None, apply_to_mask=True)
Redimensiona (atalho para vfx.Resize).

rotated(angle, unit="deg", resample="bicubic", expand=False, center=None, translate=None, bg_color=None)
Rotaciona (atalho para vfx.Rotate).

cropped(x1=None, y1=None, x2=None, y2=None, width=None, height=None, x_center=None, y_center=None)
Recorta (atalho para vfx.Crop).

Conversões

to_ImageClip(t=0, with_mask=True, duration=None)
Captura um ImageClip do frame em t.

to_mask(canal=0)
Converte para clip de máscara (escala [0..1]), derivando de um canal.

to_RGB()
Converte máscara em clip RGB (ou retorna self se já for RGB).

Operadores (atalhos úteis)

__add__(other) → concatenação sequencial (chain se mesmo tamanho, compose caso contrário).

__or__(other) → lado a lado horizontal (array [[self, other]]).

__truediv__(other) → empilhado vertical (array [[self], [other]]).

__matmul__(n) → atalho para rotacionar por n (graus por padrão).

__and__(mask) → define máscara do clip (self.with_mask(mask)).

Propriedades úteis

w, h → largura e altura em pixels.

aspect_ratio → w / h.

n_frames → duration * fps (requer duration e fps).

Padrões de uso recomendados

Para legendas e títulos adaptáveis em caixas: use method="caption" com size=(width, height) e deixe font_size=None para autoajuste.

Para rótulos/tags que se expandem ao conteúdo: use method="label" e informe apenas font_size ou apenas size[0] (largura) para que o outro seja inferido.

Para overlay em vídeo existente:

Crie o TextClip(..., transparent=True, bg_color=None, duration=...);

Posicione com with_position(...) e ajuste with_opacity(...) se necessário;

Componha via CompositeVideoClip([bg, text]) (fora do escopo do trecho, mas compatível).

Para exportação isolada do card de texto: save_frame("card.png") ou write_gif(...)/write_videofile(...) se animado por composições/efeitos.

Erros comuns e como evitar

ValueError: No text nor filename provided: sempre forneça text ou filename.

Fonte inválida: verifique font (caminho e extensão), ou deixe None para a fonte padrão da Pillow.

Parâmetros de method inconsistentes: em caption, exija width; em label, especifique font_size ou size[0].

Transparência não aplicada: assegure transparent=True e, se desejar fundo transparente, bg_color=None (resultará em RGBA com alfa 0).

Exemplo mínimo
from moviepy.video.VideoClip import TextClip  # conforme organização do seu projeto

title = TextClip(
    text="Agentes de IA — Aula 01",
    font="path/para/sua_fonte.ttf",
    method="caption",
    size=(1280, 200),   # largura obrigatória em caption
    bg_color=None,      # fundo transparente
    color="white",
    stroke_color="black",
    stroke_width=2,
    text_align="center",
    horizontal_align="center",
    vertical_align="center",
    interline=6,
    duration=5.0
)

# Posicionar no topo ao centro em futura composição:
title = title.with_position(("center", "top"))
# Salvar o card gerado:
title.save_frame("titulo.png")

Resumo

TextClip fornece um meio direto e controlável de criar elementos textuais estáticos com rico controle tipográfico e de layout.

Ele integra-se ao pipeline de VideoClip e ImageClip, herdando exportação, preview, composição, máscara, geometria e conversões.

A escolha entre method="label" e method="caption" define o modo de ajuste (ao conteúdo vs. à caixa).

Transparência, stroke e alinhamentos estão totalmente suportados via Pillow e expostos no clip.