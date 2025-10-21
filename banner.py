# banner.py
# Banner gradient + hiển thị version thủ công

import os, sys, shutil

ASCII = r"""
██████╗ ███████╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗    ██████╗  ██████╗ 
██╔══██╗██╔════╝████╗ ████║██╔═══██╗██║   ██║██╔════╝    ██╔══██╗██╔════╝ 
██████╔╝█████╗  ██╔████╔██║██║   ██║██║   ██║█████╗      ██████╔╝██║  ███╗
██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██╔══╝      ██╔══██╗██║   ██║
██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ███████╗    ██████╔╝╚██████╔╝
╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝    ╚═════╝  ╚═════╝ 
""".strip("\n")

COLORS = ["#00FF66", "#00E5FF", "#0077FF"]


VERSION = "2.1.0"

ALIGN_TO_BANNER_WIDTH = True  # False = căn phải theo terminal width

def enable_vt_on_windows():
    if os.name != "nt": return True
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        h = k32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if not k32.GetConsoleMode(h, ctypes.byref(mode)): return False
        if not k32.SetConsoleMode(h, mode.value | 0x0004): return False
        return True
    except: return False

def hex_to_rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return int(round(a+(b-a)*t))
def grad_color(t,c1,c2,c3):
    if t<=0.5: u=t*2; return tuple(lerp(a,b,u) for a,b in zip(c1,c2))
    u=(t-0.5)*2; return tuple(lerp(a,b,u) for a,b in zip(c2,c3))

def main():
    vt_ok = enable_vt_on_windows()
    ESC = "\x1b"
    lines = ASCII.splitlines()
    ts = [i/(len(lines)-1) if len(lines)>1 else 0 for i in range(len(lines))]
    c1,c2,c3 = map(hex_to_rgb,COLORS)

    for i,line in enumerate(lines):
        if vt_ok:
            r,g,b = grad_color(ts[i],c1,c2,c3)
            sys.stdout.write(f"{ESC}[38;2;{r};{g};{b}m{line}{ESC}[0m\n")
        else: print(line)

    if VERSION:
        r3,g3,b3 = hex_to_rgb(COLORS[-1])
        width = max(len(l) for l in lines) if ALIGN_TO_BANNER_WIDTH else shutil.get_terminal_size((80,25)).columns
        pad = max(1,width-len("v"+VERSION))
        if vt_ok:
            print(f"{ESC}[38;2;{r3};{g3};{b3}m" + " "*pad + f"v{VERSION}" + f"{ESC}[0m")
        else:
            print(" "*pad + f"v{VERSION}")

if __name__=="__main__":
    main()
