#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sailor Jupiter ASCII Art Banner for Ansible Playbooks
"""

import sys
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform color support
init(autoreset=True)

def print_sailor_jupiter():
    """Print colorful Sailor Jupiter ASCII art"""
    
    # Define the ASCII art
    jupiter_art = """
                          ⚡️✨🌸✨⚡️
                    ╔═══════════════════╗
                    ║  SAILOR JUPITER   ║
                    ╚═══════════════════╝
                         
                        .･ﾟ✧*:･ﾟ✧
                     ╱╲     ╱╲     ╱╲
                    ╱  ╲___╱  ╲___╱  ╲
                   │  ⚡  JUPITER  ⚡  │
                    ╲  ╱‾‾‾╲  ╱‾‾‾╲  ╱
                     ╲╱     ╲╱     ╲╱
                         
                      ╭──────────╮
                     │ ◉   ⚡   ◉ │
                    ╱ ╲          ╱ ╲
                   │   ╲  🌹   ╱   │
                  ╱│    ╲____╱    │╲
                 │ │  ●        ●  │ │
                 │ │      ><      │ │
                 │ │   ╲  ‿  ╱   │ │
                 │  ╲     ──     ╱  │
                  ╲  ╲__________╱  ╱
                   ╲___╱‾‾‾‾╲___╱
                      │  ⚡⚡  │
                    ╭─┴──────┴─╮
                   ╱     ⚡     ╲
                  │  MAKOTO KINO │
                   ╲_____________╱
    """
    
    # Print with colors
    lines = jupiter_art.split('\n')
    for i, line in enumerate(lines):
        if '⚡' in line:
            # Lightning bolts in bright yellow
            line = line.replace('⚡', f'{Fore.YELLOW}{Style.BRIGHT}⚡{Style.RESET_ALL}')
        if '✨' in line:
            # Sparkles in bright white
            line = line.replace('✨', f'{Fore.WHITE}{Style.BRIGHT}✨{Style.RESET_ALL}')
        if '🌸' in line:
            # Flower in pink/magenta
            line = line.replace('🌸', f'{Fore.MAGENTA}{Style.BRIGHT}🌸{Style.RESET_ALL}')
        if '🌹' in line:
            # Rose in red
            line = line.replace('🌹', f'{Fore.RED}{Style.BRIGHT}🌹{Style.RESET_ALL}')
        
        # Color different parts of the face
        if '●' in line:
            # Eyes in green (Jupiter's color)
            line = line.replace('●', f'{Fore.GREEN}{Style.BRIGHT}●{Style.RESET_ALL}')
        if '◉' in line:
            # Tiara gems in cyan
            line = line.replace('◉', f'{Fore.CYAN}{Style.BRIGHT}◉{Style.RESET_ALL}')
        
        # Hair/crown lines in brown/green
        if '╱' in line or '╲' in line or '│' in line:
            if i < 10:  # Upper part (hair)
                print(f'{Fore.GREEN}{line}{Style.RESET_ALL}')
            else:
                print(f'{Fore.WHITE}{line}{Style.RESET_ALL}')
        elif 'SAILOR JUPITER' in line:
            print(f'{Fore.YELLOW}{Style.BRIGHT}{line}{Style.RESET_ALL}')
        elif 'MAKOTO KINO' in line:
            print(f'{Fore.GREEN}{Style.BRIGHT}{line}{Style.RESET_ALL}')
        else:
            print(line)
    
    # Print her famous quotes with effects
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{'═' * 60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}  'Supreme Thunder!' ⚡ 'Sparkling Wide Pressure!' ✨{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}     'I am the Pretty Guardian who fights for{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}            Love and Courage!'{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}{'═' * 60}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    print_sailor_jupiter()