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
    
    # Define the ASCII art with magical symbols
    jupiter_art = """
                    ✧･ﾟ: *✧･ﾟ:* 🌙 *:･ﾟ✧*:･ﾟ✧
                  ⋆｡‧˚ʚ♡ɞ˚‧｡⋆  ⚡  ⋆｡‧˚ʚ♡ɞ˚‧｡⋆
                         
     ╔═════════════════════════════════════════════════════╗
     ║                                                     ║
     ║   ███████  █████  ██ ██      ████  ██████           ║
     ║   ██      ██   ██ ██ ██     ██  ██ ██   ██          ║
     ║   ███████ ███████ ██ ██     ██  ██ ██████           ║
     ║        ██ ██   ██ ██ ██     ██  ██ ██   ██          ║
     ║   ███████ ██   ██ ██ ██████  ████  ██   ██          ║
     ║                                                     ║
     ║        ██ ██  ██ ██████  ██ ████████ ██████ ██████  ║
     ║        ██ ██  ██ ██   ██ ██    ██    ██     ██   ██ ║
     ║        ██ ██  ██ ██████  ██    ██    █████  ██████  ║
     ║   ██   ██ ██  ██ ██      ██    ██    ██     ██   ██ ║
     ║    █████   ████  ██      ██    ██    ██████ ██   ██ ║
     ║                                                     ║
     ╚═════════════════════════════════════════════════════╝
                         
                   ⚡ ════════════════════ ⚡
                  ✨  Guardian of Thunder  ✨
                  🌸   Protector of Love   🌸
                   ⚡ ════════════════════ ⚡
                         
               ･ﾟ✧*:･ﾟ✧ 木野 まこと ✧･ﾟ: *✧･ﾟ:*
                         (Makoto Kino)
                         
            ╭─────────────────────────────────────╮
            │  ⋆˚✿˖° Jupiter Crystal Power °˖✿˚⋆  │
            ╰─────────────────────────────────────╯
    """
    
    # Print with colors
    lines = jupiter_art.split('\n')
    for i, line in enumerate(lines):
        # Replace symbols with colored versions
        if '⚡' in line:
            # Lightning bolts in bright yellow
            line = line.replace('⚡', f'{Fore.YELLOW}{Style.BRIGHT}⚡{Style.RESET_ALL}')
        if '✨' in line:
            # Sparkles in bright white
            line = line.replace('✨', f'{Fore.WHITE}{Style.BRIGHT}✨{Style.RESET_ALL}')
        if '🌸' in line:
            # Flower in pink/magenta
            line = line.replace('🌸', f'{Fore.MAGENTA}{Style.BRIGHT}🌸{Style.RESET_ALL}')
        if '🌙' in line:
            # Moon in cyan
            line = line.replace('🌙', f'{Fore.CYAN}{Style.BRIGHT}🌙{Style.RESET_ALL}')
        if '☆' in line or '⋆' in line:
            # Stars in bright white
            line = line.replace('☆', f'{Fore.WHITE}{Style.BRIGHT}☆{Style.RESET_ALL}')
            line = line.replace('⋆', f'{Fore.WHITE}{Style.BRIGHT}⋆{Style.RESET_ALL}')
        if '♡' in line:
            # Hearts in red
            line = line.replace('♡', f'{Fore.RED}{Style.BRIGHT}♡{Style.RESET_ALL}')
        if '✿' in line:
            # Flowers in magenta
            line = line.replace('✿', f'{Fore.MAGENTA}{Style.BRIGHT}✿{Style.RESET_ALL}')
        
        # Color the ASCII text blocks (SAILOR JUPITER)
        if '█' in line:
            # Make the block letters green (Jupiter's color)
            print(f'{Fore.GREEN}{Style.BRIGHT}{line}{Style.RESET_ALL}')
        elif 'Guardian of Thunder' in line:
            print(f'{Fore.YELLOW}{Style.BRIGHT}{line}{Style.RESET_ALL}')
        elif 'Protector of Love' in line:
            print(f'{Fore.MAGENTA}{Style.BRIGHT}{line}{Style.RESET_ALL}')
        elif 'Jupiter Crystal Power' in line:
            print(f'{Fore.CYAN}{Style.BRIGHT}{line}{Style.RESET_ALL}')
        elif '木野 まこと' in line or 'Makoto Kino' in line:
            print(f'{Fore.GREEN}{Style.BRIGHT}{line}{Style.RESET_ALL}')
        elif '═' in line:
            # Make horizontal lines yellow for thunder theme
            print(f'{Fore.YELLOW}{line}{Style.RESET_ALL}')
        elif '╔' in line or '╗' in line or '╚' in line or '╝' in line or '║' in line:
            # Box borders in green
            print(f'{Fore.GREEN}{line}{Style.RESET_ALL}')
        elif '╭' in line or '╮' in line or '╰' in line or '╯' in line:
            # Rounded borders in cyan
            print(f'{Fore.CYAN}{line}{Style.RESET_ALL}')
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
