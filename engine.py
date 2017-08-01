from input_handlers import handle_keys, handle_mouse
from render_functions import clear_all, render_all
from entity import get_blocking_entities_at_location
from game_states import GameStates
from death_functions import kill_monster, kill_player
from game_messages import Message
from loader_functions.initialize_new_game import get_constants, get_game_variables
import tdl

def main():
    constants = get_constants()

    tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)
    root_console = tdl.init(constants['screen_width'], constants['screen_height'], constants['window_title'])
    con = tdl.Console(constants['screen_width'], constants['screen_height'])
    panel = tdl.Console(constants['screen_width'], constants['panel_height'])

    fov_recompute = True

    player, entities, game_map, message_log, game_state = get_game_variables(constants)

    mouse_coordinates = (0, 0)

    previous_game_state = game_state

    targeting_item = None

    while not tdl.event.is_window_closed():
        if fov_recompute:
            game_map.compute_fov(player.x, player.y, fov=constants['fov_algorithm'], radius=constants['fov_radius'], light_walls=constants['fov_light_walls'])

        render_all(con, panel, entities, player, game_map, fov_recompute, root_console, message_log, constants['screen_width'], constants['screen_height'],
                bar_width, constants['panel_height'], constants['panel_y'], mouse_coordinates, constants['colors'], game_state)

        tdl.flush()

        clear_all(con, entities)

        fov_recompute = False

        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                user_input = event
                break
            elif event.type == 'MOUSEMOTION':
                mouse_coordinates = event.cell
            elif event.type == 'MOUSEDOWN':
                user_mouse_input = event
                break
        else:
            user_input = None
            user_mouse_input = None

        if not (user_input or user_mouse_input):
            continue

        action = handle_keys(user_input, game_state)
        mouse_action = handle_mouse(user_mouse_input)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if game_map.walkable[destination_x, destination_y]:
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)

                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity, constants['colors'])
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', constants['colors'].get('yellow')))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, constants['colors'], entities=entities, game_map=game_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item, constants['colors']))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, constants['colors'], entities=entities, game_map=game_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                return True

        if fullscreen:
            tdl.set_fullscreen(not tdl.get_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity, constants['colors'])
                else:
                    message = kill_monster(dead_entity, constants['colors'])

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity, constants['colors'])
                            else:
                                message = kill_monster(dead_entity, constants['colors'])

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN

if __name__ == '__main__':
    main()
