import tdl
import textwrap

def menu(con, root, header, options, width, screen_width, screen_height):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    header_wrapped = textwrap.wrap(header, width)
    header_height = len(header_wrapped)
    height = len(options) + header_height

    window = tdl.Console(width, height)
    
    window.draw_rect(0, 0, width, height, None, fg=(255, 255, 255), bg=None)
    for i, line in enumerate(header_wrapped):
        window.draw_str(0, 0 + i, header_wrapped[i])

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '({}) {}'.format(chr(letter_index), option_text)
        window.draw_str(0, y, text, bg=None)
        y += 1
        letter_index += 1

    x = screen_width // 2 - width // 2
    y = screen_height // 2 - height // 2
    root.blit(window, x, y, width, height, 0, 0)

def inventory_menu(con, root, header, inventory, inventory_width, screen_width, screen_height):
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]

    menu(con, root, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, root_console, background_image, screen_width, screen_height, colors):
    background_image.blit_2x(root_console, 0, 0)

    title = 'TOMBS OF THE ANCIENT KINGS'
    center = (screen_width - len(title)) // 2
    root_console.draw_str(center, screen_height // 2 - 4, title, bg=None, fg=colors.get('light_yellow'))

    title = 'By Robert Bond'
    center = (screen_width - len(title)) // 2
    root_console.draw_str(center, screen_height - 2, title, bg=None, fg=colors.get('light_yellow'))

    menu(con, root_console, '', ['Play a new game', 'Continue last game', 'Quit'], 24, screen_width, screen_height)

def level_up_menu(con, root, header, player, menu_width, screen_width, screen_height):
    options = [
        'Constitution (+20 HP, from {})'.format(player.fighter.max_hp),
        'Strength (+1 attack, from {})'.format(player.fighter.power),
        'Agility (+1 defense, from {})'.format(player.fighter.defense)
    ]

    menu(con, root, header, options, menu_width, screen_width, screen_height)

def character_screen(root_console, player, character_screen_width, character_screen_height, screen_width, screen_height):
    window = tdl.Console(character_screen_width, character_screen_height)

    window.draw_rect(0, 0, character_screen_width, character_screen_height, None, fg=(255, 255, 255), bg=None)

    window.draw_str(0, 1, 'Character Information')
    window.draw_str(0, 2, 'Level: {}'.format(player.level.current_level))
    window.draw_str(0, 3, 'Experience: {}'.format(player.level.current_xp))
    window.draw_str(0, 4, 'Experience to Level: {}'.format(player.level.experience_to_next_level))
    window.draw_str(0, 6, 'Maximum HP: {}'.format(player.fighter.max_hp))
    window.draw_str(0, 7, 'Attack: {}'.format(player.fighter.power))
    window.draw_str(0, 8, 'Defense: {}'.format(player.fighter.defense))

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    root_console.blit(window, x, y, character_screen_width, character_screen_height, 0, 0)

def message_box(con, root_console, header, width, screen_width, screen_height):
    menu(con, root_console, header, [], width, screen_width, screen_height)
