
#PxPlus ToshibaTxL1 8x16
from blessed import Terminal
import os
term = Terminal()
import sys
if os.name == 'nt':
    try:
        import ctypes
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        handle = ctypes.windll.kernel32.GetStdHandle(-11) 
        mode = ctypes.c_ulong(0)
        ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
        ctypes.windll.kernel32.SetConsoleMode(handle, mode)        
    except Exception:
        pass
def clear():
    print(term.home + term.clear_eos, end="")
def clear_region_a(x, start_y, end_y, width):
    if end_y < start_y:
        start_y, end_y = end_y, start_y 
    empty_line = ' ' * width
    for y in range(start_y, end_y + 1):
        print(term.move_xy(x, y) + empty_line)

def draw_window(term, x, y, width, height, title='', text_content='', bg_color='default'):
    if bg_color == 'default':
        bg_style = ''
    else:
        bg_style = getattr(term, f'on_{bg_color}', '')
    border_style = bg_style + term.white_on_default 
    title_style = bg_style + term.bold_on_default
    text_style = bg_style + term.on_default
    with term.location(x, y):
        print(border_style + '╔' + '═' * (width - 2) + '╗' + term.normal)
    for i in range(1, height - 1):
        with term.location(x, y + i):
            print(text_style + '║' + ' ' * (width - 2) + '║' + term.normal)
    with term.location(x, y + height - 1):
        print(border_style + '╚' + '═' * (width - 2) + '╝' + term.normal)
    if title:
        title_x = x + (width - len(title)) // 2
        with term.location(title_x, y):
            print(title_style + ' ' + title + ' ' + term.normal)
    if text_content:
        lines = text_content.split('\n')
        for i, line in enumerate(lines):
            if i < height - 2:
                with term.location(x + 2, y + i + 1):
                    print(text_style + line[:width - 4] + term.normal)

class Cores:
    PRETO = '\033[30m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    MAGENTA = '\033[35m'
    CIANO = '\033[36m'
    CINZA_CLARO = '\033[37m'
    CINZA_ESCURO = '\033[90m'
    VERMELHO_CLARO = '\033[91m'
    FUNDO_PRETO = '\033[40m'
    FUNDO_VERDE = '\033[42m'
    FUNDO_BRANCO = '\033[47m'
    FUNDO_MARROM = '\033[48;5;94m'
    CLEAR = '\033[H\033[J'
    RESET = '\033[0m'
    BRILHO = '\033[1m'
    INVERTER = '\033[7m'
C = Cores

class art_ascii:
    def __init__(self):
        self.suny = r"""    \|/            \|/
    /v\   (    )   /v\
   /v v\  |\^^/|  /v v\
  /v/v\v\_(@::@)_/v/v\v\
 /v/v v\v  \\//  v/v v\v\
(v v v v v (oo) v v v v v)
 \v /V\ v v/  \v v /V\ v/
  \/   \ v/    \v /   \/
        \/      \/
"""
        self.zombie = r"""          __ _
        .'  Y '>,
        / _   _  \
        )(_) (_)(|}
        {  4A   } /
        \uLuJJ/\l
        |3    p)/
        /nnm_n//
        \_>-<_/D"""
        self.musumano = r"""  |
      |
      + \
      \\.G_.*=.
       `(#'/.\|
        .>' (_--.
     _=/d   ,^\
    ~~ \)-'   '
       / |   
      '  '
"""
        self.titulo = f"""
{C.AMARELO+C.BRILHO}                            ╔╦╗┬ ┬┌─┐ 
{C.AMARELO+C.BRILHO}                             ║ ├─┤├┤  
{C.AMARELO+C.BRILHO}                             ╩ ┴ ┴└─┘
{C.CINZA_CLARO+C.BRILHO}                        ╦┌─┐┬  ┌─┐┌┐┌┌┬┐
{C.CINZA_CLARO+C.BRILHO}                        ║└─┐│  ├─┤│││ ││
{C.CINZA_CLARO+C.BRILHO}                        ╩└─┘┴─┘┴ ┴┘└┘─┴┘                        
"""
        self.necro = r""" (\.   \      ,/)
  \(   |\     )/
  //\  | \   /\\
 (/ /\_#oo#_/\ \)
  \/\__####__/\/
       \##/
       /##\
      /####\
      \~~~~/
"""
        self.mago = r"""         ,/   *
      _,'/_   |
      `(")' ,'/
   _ _,-H-./ /
   \_\_\.   /
     )" |  (
  __/   H   \__
  \    /|\    /
   `--'|||`--'
      ==^=="""
        self.esqueleto = r"""        .-.
       (o.o)
        |=|
       __|__
     //.=|=.\\
    // .=|=. \\
    \\ .=|=. //
     \\(_=_)//
      (:| |:)
       || ||
       () ()
       || ||
       || ||
      ==' '==
"""
        self.demoni0 = r'''   ,    ,    /\   /\
  /( /\ )\  _\ \_/ /_
  |\_||_/| < \_   _/ >
  \______/  \|0   0|/
    _\/_   _(_  ^  _)_
   ( () ) /`\|V"""V|/`\
     {}   \  \_____/  /
     ()   /\   )=(   /\
     {}  /  \_/\=/\_/  \ 
'''
        self.demoni1 = r"""            v
      (__)v | v
      /\/\\_|_/
     _\__/  |
    /  \/`\<`)
    \ (  |\_/
   /)))-(  |
  / /^ ^ \ |
 /  )^/\^( |
 )_//`__>> |
   #   #`  | 
"""
        self.guerriro = r"""                 /
          ,~~   /
      _  <=)  _/_
     /I\.="==.{>
     \I/-\T/-'
         /_\
        // \\_
       _I    / 
============================
"""
        self.serafas = r'''
          /
     /\   |
    /  \  |/
   |    | |>
   \____/ |
   ( .. ) |
   /\__/\ |
  /\ qp /\|
 /  |  |  |
/|  |db| /\`\
| \ |  | \|_|
\  \|qp|  |
 \__/  |  |
 |/||db|  |
 |  |  |  |
'''


art = art_ascii()

class mini_mapa_:
    def __init__(self):
        self.igreja = r"""

"""

class dialogos:
    def __init__(self):
        self.padre_1 = 'Rapaz não me pertube no monento estou tentando me consentrar no momento depois converse comigo'
        self.padre_2 = 'Rapaz dessa para a caverna e derrote o dragão Suny ele fica no decimo andar depois converse comigo'
        self.padre_3 = 'Rapaz o mundo está em calçus porem você e eu estamos calmo é estranho persar isso'
        self.padre_4 = 'Pelo visto você realmente matou o Dragão Suny então se quiser posso te encinar a arte as magias milenares'
        self.aldao_1 = 'Você é um andariolho? isso é estranho pensei que todos os fora da grande cupula aviam morrido'
        self.aldao_2 = 'Você pode plantar coisa usando uma enchada e uma pá para abrir burracos para achar sementes'
        self.aldao_3 = 'Utilize a bancada para fazer tudo oque você quiser'
        self.aldao_4 = 'Com a derrota do Dragão Suny algumas estruturas apareceram no mundo o senhor dos Céus Serefas será o primeiro'
        self.aldao_5 = 'Você pode ir as novas construções por lá terá novos bosses'