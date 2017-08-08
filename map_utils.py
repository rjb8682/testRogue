from tdl.map import Map
from random import randint
from entity import Entity
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from render_functions import RenderOrder
from item_functions import cast_confuse, cast_lightning, cast_fireball, heal
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
    for y in range(min(y1, y2), min(y1, y2) + 1):
        game_map.walkable[x, y] = True
        game_map.transparent[x, y] = True

def place_entities(game_map, room, entities, max_monsters_per_room, max_items_per_room, colors):
    number_of_monsters = randint(0, max_monsters_per_room)
    number_of_items = randint(0, max_items_per_room)

    for i in range(number_of_monsters):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            monster_chance = randint(0, 100)

            if monster_chance < 80:
                fighter_component = Fighter(hp=10, defense=0, power=3, xp=35)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'o', colors.get('bright_green'), 'Orc', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
            elif monster_chance < 90:
                fighter_component = Fighter(hp=16, defense=1, power=4, xp=100)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'T', colors.get('bright_red'), 'Troll', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
            elif monster_chance < 95:
                fighter_component = Fighter(hp=7, defense=1, power=6, xp=130)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'K', colors.get('light_red'), 'Kobold', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=20, defense=2, power=4, xp=150)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'G', colors.get('green'), 'Golem', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

            entities.append(monster)

    for i in range(number_of_items):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]) and game_map.walkable[x, y]:
            item_chance = randint(0, 100)

            if item_chance < 70:
                item_component = Item(use_function=heal, amount=4)
                item = Entity(x, y, '!', colors.get('bright_orange'), 'Healing Potion', render_order=RenderOrder.ITEM, item=item_component)
            elif item_chance < 80:
                item_component = Item(use_function=cast_fireball, targeting=True,
                                      targeting_message=Message('Left-click a target tile for the fireball, or right-click to cancel.', colors.get('light_cyan')), damage=12, radius=3)
                item = Entity(x, y, '#', colors.get('red'), 'Fireball Scroll', render_order=RenderOrder.ITEM, item=item_component)
            elif item_chance < 90:
                item_component = Item(use_function=cast_confuse, targeting=True,
                                      targeting_message=Message('Left-click an enemy to confuse it, or right-click to cancel.', colors.get('light_cyan')))
                item = Entity(x, y, '#', colors.get('light_pink'), 'Confusion Scroll', render_order=RenderOrder.ITEM, item=item_component)
            else:
                item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
                item = Entity(x, y, '#', colors.get('yellow'), 'Lightning Scroll', render_order=RenderOrder.ITEM, item=item_component)

            entities.append(item)

def make_map(game_map, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
        max_monsters_per_room, max_items_per_room, colors):
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

            place_entities(game_map, new_room, entities, max_monsters_per_room, max_items_per_room, colors)

            rooms.append(new_room)
            num_rooms += 1

    stairs_component = Stairs(game_map.dungeon_level + 1)
    down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', colors.get('white'), 'Stairs', render_order=RenderOrder.STAIRS, stairs=stairs_component)
    entities.append(down_stairs)

def next_floor(player, message_log, dungeon_level, constants):
    game_map = GameMap(constants['map_width'], constants['map_height'], dungeon_level)
    entities = [player]

    make_map(game_map, constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player,
             entities, constants['max_monsters_per_room'], constants['max_items_per_room'], constants['colors'])

    player.fighter.heal(player.fighter.max_hp // 2)
    message_log.add_message(Message('You take a moment to rest, and recover your strength.', constants['colors'].get('light_violet')))

    return game_map, entities
