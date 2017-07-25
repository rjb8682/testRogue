def handle_keys(user_input):
    if user_input.key == 'UP' or (user_input.key == 'CHAR' and user_input.char == 'k'):
        return {
            'move': (0, -1)
        }
    elif user_input.key == 'DOWN' or (user_input.key == 'CHAR' and user_input.char == 'j'):
        return {
            'move': (0, 1)
        }
    elif user_input.key == 'LEFT' or (user_input.key == 'CHAR' and user_input.char == 'h'):
        return {
            'move': (-1, 0)
        }
    elif user_input.key == 'RIGHT' or (user_input.key == 'CHAR' and user_input.char == 'l'):
        return {
            'move': (1, 0)
        }

    if user_input.key == 'ENTER' and user_input.alt:
        return {
            'fullscreen': True
        }
    elif user_input.key == 'ESCAPE':
        return {
            'exit': True
        }

    return {}
