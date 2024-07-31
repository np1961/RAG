
from time import sleep
from sys import stdout
from sys import path

from colorama import Fore as COLORS_FRONT
from colorama import Back as COLORS_BACK

def change_colors(index_front=0 , index_back=0):

    colors_names=['RESET','BLUE', 'GREEN', 'MAGENTA', 'RED', 'WHITE', 'YELLOW']
    
    index_front=index_front%len(colors_names)
    index_back=index_back%len(colors_names)

    color_front_name=colors_names[index_front]
    color_back_name=colors_names[index_back]
    
    color_front=COLORS_FRONT.__dict__[color_front_name]
    color_back=COLORS_BACK.__dict__[color_back_name]

    stdout.write(color_front)
    stdout.write(color_back)
    
    


def terminal_write(text=None,
                   time_sleep=0.0061,
                   endl=True,
                   index_front=0,
                   index_back=0,
                   colors=(0,0)
                                   ):
    if text is None:
        text,colors =(text if text is not None else "".join(str(_) for _ in range(19)) , (3,3))

    index_back, index_front=colors if (index_back,index_front)==(0,0) else (index_back,index_front)
    change_colors(index_front=index_front, index_back=index_back)
    
    text=text if not endl else f"{text}\n"
    
    for _text_ in text:
        stdout.write(_text_)
        stdout.flush()
        sleep(time_sleep)
        

    
    
        
