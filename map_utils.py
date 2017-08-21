from tdl.map import Map
from random import randint
from entity import Entity
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from equipment_slots import EquipmentSlots
from components.equippable import Equippable
from components.stairs import Stairs
from render_functions import RenderOrder
from item_functions import cast_confuse, cast_lightning, cast_fireball, heal
from random_utils import from_dungeon_level, random_choice_from_dict
from game_messages import Message

class GameMap(Map):
    def __init__(self, width, height, dungeon_level=1):
        super().__init__(width, height)
        self.explored = [[False for y in range(height)] for x in range(width)]
        self.dungeon_level = dungeon_level

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

def create_room(game_map, room):
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            game_map.walkable[x, y] = True
            game_map.transparent[x, y] = True

def create_h_tunnel(game_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        game_map.walkable[x, y] = True
        game_map.transparent[x, y] = True

def create_v_tunnel(game_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        game_map.walkable[x, y] = True
        game_map.transparent[x, y] = True

def place_entities(game_map, room, entities, colors):
    dungeon_level = game_map.dungeon_level
    max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], dungeon_level)
    max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], dungeon_level)

    number_of_monsters = randint(0, max_monsters_per_room)
    number_of_items = randint(0, max_items_per_room)

    monster_chances = {
        'orc': 80,
        'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], dungeon_level),
        'kobold': from_dungeon_level([[20, 3], [30, 5], [50, 7]], dungeon_level),
        'golem': from_dungeon_level([[20, 5], [30, 8]], dungeon_level)
    }

    item_chances = {
        'healing_potion': 40,
        'sword': from_dungeon_level([[5, 4]], dungeon_level),
        'shield': from_dungeon_level([[15, 2]], dungeon_level),
        'lightning_scroll': from_dungeon_level([[25, 3], [35, 6]], dungeon_level),
        'fireball_scroll': from_dungeon_level([[25, 4], [35, 7]], dungeon_level),
        'confusion_scroll': from_dungeon_level([[30, 5]], dungeon_level)
    }

    for i in range(number_of_monsters):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            monster_choice = random_choice_from_dict(monster_chances)

            if monster_choice == 'orc':
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'o', colors.get('bright_green'), 'Orc', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
            elif monster_choice == 'troll':
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'T', colors.get('bright_red'), 'Troll', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
            elif monster_choice == 'kobold':
                fighter_component = Fighter(hp=15, defense=1, power=14, xp=130)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'K', colors.get('light_red'), 'Kobold', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=45, defense=3, power=6, xp=150)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'G', colors.get('green'), 'Golem', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

            entities.append(monster)

    for i in range(number_of_items):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        same_location_entities = [entity for entity in entities if entity.x == x and entity.y == y]

        if len(same_location_entities) == 0 and game_map.walkable[x, y]:
            item_choice = random_choice_from_dict(item_chances)

            if item_choice == 'healing_potion':
                item_component = Item(use_function=heal, amount=40)
                item = Entity(x, y, '!', colors.get('bright_orange'), 'Healing Potion', render_order=RenderOrder.ITEM, item=item_component)
            elif item_choice == 'sword':
                equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                item = Entity(x, y, '/', colors.get('sky'), 'Sword', equippable=equippable_component)
            elif item_choice == 'shield':
                equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                item = Entity(x, y, '[', colors.get('darker_orange'), 'Shield', equippable=equippable_component)
            elif item_choice == 'fireball_scroll':
                item_component = Item(use_function=cast_fireball, targeting=True,
                                      targeting_message=Message('Left-click a target tile for the fireball, or right-click to cancel.', colors.get('light_cyan')), damage=25, radius=3)
                item = Entity(x, y, '#', colors.get('red'), 'Fireball Scroll', render_order=RenderOrder.ITEM, item=item_component)
            elif item_choice == 'confusion_scroll':
                item_component = Item(use_function=cast_confuse, targeting=True,
                                      targeting_message=Message('Left-click an enemy to confuse it, or right-click to cancel.', colors.get('light_cyan')))
                item = Entity(x, y, '#', colors.get('light_pink'), 'Confusion Scroll', render_order=RenderOrder.ITEM, item=item_component)
            else:
                item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                item = Entity(x, y, '#', colors.get('yellow'), 'Lightning Scroll', render_order=RenderOrder.ITEM, item=item_component)

            entities.append(item)

def make_map(game_map, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, colors):
    rooms = []
    num_rooms = 0

    center_of_last_room_x = None
    center_of_last_room_y = None

    for r in range(max_rooms):
        w = randint(room_min_size, room_max_size)
        h = randint(room_min_size, room_max_size)

        x = randint(0, map_width - w - 1)
        y = randint(0, map_height - h - 1)

        new_room = Rect(x, y, w, h)

        for other_room in rooms:
            if new_room.intersect(other_room):
                break

        else:
            create_room(game_map, new_room)
            (new_x, new_y) = new_room.center()

            center_of_last_room_x = new_x
            center_of_last_room_y = new_y

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                if randint(0, 1) == 1:
                    create_h_tunnel(game_map, prev_x, new_x, prev_y)
                    create_v_tunnel(game_map, prev_y, new_y, new_x)
                else:
                    create_v_tunnel(game_map, prev_y, new_y, prev_x)
                    create_h_tunnel(game_map, prev_x, new_x, new_y)

            place_entities(game_map, new_room, entities, colors)

            rooms.append(new_room)
            num_rooms += 1

    stairs_component = Stairs(game_map.dungeon_level + 1)
    down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', colors.get('white'), 'Stairs', render_order=RenderOrder.STAIRS, stairs=stairs_component)
    entities.append(down_stairs)

def next_floor(player, message_log, dungeon_level, constants):
    game_map = GameMap(constants['map_width'], constants['map_height'], dungeon_level)
    entities = [player]

    make_map(game_map, constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player, entities, constants['colors'])

    player.fighter.heal(player.fighter.max_hp // 2)
    message_log.add_message(Message('You take a moment to rest, and recover your strength.', constants['colors'].get('light_violet')))

    return game_map, entities
