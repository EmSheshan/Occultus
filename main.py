import json
import random
import sys
import math
import pyautogui
import pygame
from pygame.locals import *
import monster
import moves

pygame.init()

fps = 60
fpsClock = pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
# SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
MARGIN = SCREEN_HEIGHT//54
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Occultus - DEV")

font_size = round(36 * (SCREEN_WIDTH / 1920))
font = pygame.font.Font('assets/Mono a Mano.ttf', font_size)

background_image = pygame.image.load("assets/Background.png").convert()
temple_image = pygame.image.load("assets/Temple.png").convert_alpha()
shadow_image = pygame.image.load("assets/Shadow.png").convert_alpha()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
temple_image = pygame.transform.scale(temple_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
shadow_image = pygame.transform.scale(shadow_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Before the game loop
background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create a surface to render the background
background_surface.blit(background_image, (0, 0))  # Blit the background image onto the surface
background_surface.blit(temple_image, (0, 0))
background_surface.blit(shadow_image, (0, 0))


whole_icon_surface = pygame.image.load('assets/press_icon_full.png')
half_icon_surface = pygame.image.load('assets/press_icon_half.png')

# Game audio
mp3_file = "assets/Sky Searcher.mp3"  # Replace with your MP3 file path
pygame.mixer.music.load(mp3_file)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.8)

# Load sound effects
click_sound = pygame.mixer.Sound("assets/click.wav")
defeat_sound = pygame.mixer.Sound("assets/explosion.wav")
hurt_sound = pygame.mixer.Sound("assets/hitHurt.wav")
spell_sound = pygame.mixer.Sound("assets/laserShoot.wav")
heal_sound = pygame.mixer.Sound("assets/powerUp.wav")


# Define the two colors between which SELECT_COLOR will pulsate
SELECT_COLOR1 = (255, 80, 50)
SELECT_COLOR2 = (255, 50, 80)


def pulsate_color():
    # Calculate the pulsating factor using a sine function
    pulsating_factor = (math.sin(pygame.time.get_ticks() / 400) + 1) / 2
    # Interpolate between SELECT_COLOR1 and SELECT_COLOR2 based on the pulsating factor
    pulsating_color = (
        int(SELECT_COLOR1[0] * (1 - pulsating_factor) + SELECT_COLOR2[0] * pulsating_factor),
        int(SELECT_COLOR1[1] * (1 - pulsating_factor) + SELECT_COLOR2[1] * pulsating_factor),
        int(SELECT_COLOR1[2] * (1 - pulsating_factor) + SELECT_COLOR2[2] * pulsating_factor)
    )
    return pulsating_color


def render_background():
    screen.fill((120, 120, 120))
    screen.blit(background_surface, (0, 0))


def render_health_bars():
    for i, c in enumerate(characters):
        text_surface = font.render(f"{c.name} HP: [{c.hp}/{c.max_hp}]", True,
                                   (255, 255, 255))
        screen.blit(text_surface, (MARGIN, MARGIN + i * MARGIN*2))

    text_surface = font.render(f"Current floor: {battle_count}", True, (255, 255, 255))
    screen.blit(text_surface, (SCREEN_WIDTH - text_surface.get_width() - MARGIN, MARGIN))


def render_primary_text(text, confirm=True):
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(bottomleft=(MARGIN, SCREEN_HEIGHT - MARGIN))
    box_rect = pygame.Rect(MARGIN//2, SCREEN_HEIGHT - text_surface.get_height() - MARGIN*1.5,
                           text_surface.get_width() + MARGIN, text_surface.get_height() + MARGIN)  # Box around the text
    pygame.draw.rect(screen, (6, 6, 12), box_rect, 0)  # Draw the box
    screen.blit(text_surface, text_rect)
    if confirm:
        for events in pygame.event.get():
            if events.type == KEYDOWN:
                if events.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if events.key == K_SPACE or events.key == K_RETURN:
                    return True

            else:
                return False


def render_press_turn_icons():
    text_surface = font.render("", True, (255, 255, 255))
    text_rect = text_surface.get_rect(topleft=(SCREEN_WIDTH // 1.8, MARGIN))  # Adjusted position to top center
    spacing = MARGIN//4
    for i in range(whole_press_turn_count):
        screen.blit(whole_icon_surface, (SCREEN_WIDTH // 1.8 + i * (whole_icon_surface.get_width() + spacing), MARGIN))
    for i in range(half_press_turn_count):
        screen.blit(half_icon_surface, (SCREEN_WIDTH // 1.8 + (whole_press_turn_count+i) *
                                        (half_icon_surface.get_width() + spacing), MARGIN))
    screen.blit(text_surface, text_rect)


def render_action_menu(char, menu_option):
    menu_options = char.moves
    menu_height = len(menu_options) * MARGIN*2
    menu_top = SCREEN_HEIGHT - menu_height - MARGIN

    for i, option in enumerate(menu_options):
        color = (255, 255, 255)  # Default color
        if i == menu_option:
            color = SELECT_COLOR  # Highlighted color
        text_surface = font.render(f"{i + 1}: {option}", True, color)
        screen.blit(text_surface, (MARGIN, menu_top - SCREEN_HEIGHT//9 + i * MARGIN*2))


def choose_action(char, menu_option):
    render_action_menu(char, menu_option)

    for events in pygame.event.get():
        if events.type == KEYDOWN:
            if events.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if events.key == K_UP:
                menu_option = (menu_option - 1) % len(char.moves)
            elif events.key == K_DOWN:
                menu_option = (menu_option + 1) % len(char.moves)
            elif events.key == K_SPACE or events.key == K_RETURN:
                click_sound.play()
                return menu_option, True
    return menu_option, False


def render_choose_enemy(targets, menu_option):
    menu_height = len(targets) * MARGIN*2
    menu_top = SCREEN_HEIGHT - menu_height - MARGIN

    for i, e in enumerate(targets):
        color = (255, 255, 255)  # Default color
        if i == menu_option:
            color = SELECT_COLOR  # Highlighted color
        text_surface = font.render(f"{i + 1}: {e.name}", True, color)
        screen.blit(text_surface, (MARGIN, menu_top - SCREEN_HEIGHT//9 + i * MARGIN*2))


def choose_target(targets, menu_option):
    render_choose_enemy(targets, menu_option)

    for events in pygame.event.get():
        if events.type == KEYDOWN:
            if events.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if events.key == K_UP:
                menu_option = (menu_option - 1) % len(targets)
            elif events.key == K_DOWN:
                menu_option = (menu_option + 1) % len(targets)
            elif events.key == K_SPACE or events.key == K_RETURN:
                click_sound.play()
                return menu_option, True
    return menu_option, False


class Monster:
    def __init__(self, monster_reference, level):
        self.name = monster_reference.name
        self.level = level
        self.max_hp = math.ceil(monster_reference.max_hp * level / 13)
        self.hp = self.max_hp
        self.max_mp = math.ceil(monster_reference.max_mp * level / 13)
        self.mp = self.max_mp
        self.strength = math.ceil(monster_reference.strength * level / 13)
        self.magic = math.ceil(monster_reference.magic * level / 13)
        self.vitality = math.ceil(monster_reference.vitality * level / 13)
        self.agility = math.ceil(monster_reference.agility * level / 13)
        self.luck = math.ceil(monster_reference.luck * level / 13)
        self.moves = monster_reference.moves
        self.weakness = monster_reference.weakness


def calculate_damage(attacker, attack_move, whole_press_turn, half_press_turn):
    is_crit = False
    if attack_move.element == "phys":
        hurt_sound.play()
        damage = int(attacker.strength * attack_move.power)
        if random.random() < attack_move.critrate * 0.05 + attacker.luck / 100:    # Check for critical hit
            damage = int(damage * 1.5)
            if whole_press_turn > 0:
                whole_press_turn -= 1
                half_press_turn += 1
            else:
                half_press_turn -= 1
            is_crit = True
        else:
            if half_press_turn > 0:
                half_press_turn -= 1
            else:
                whole_press_turn -= 1
    else:   # Magic attack
        spell_sound.play()
        damage = attacker.magic * attack_move.power
    return whole_press_turn, half_press_turn, int(damage), is_crit


def attack(self, target, damage, element, whole_press_turn, half_press_turn, is_crit):
    message = ""
    # Check if the target reflects element
    if target.weakness[element] == "reflect":
        # Inflict damage on self equal to the damage that would have been dealt
        damage_taken = max(damage - target.vitality // 1.8, 1)
        damage_taken = int(damage_taken)
        self.hp -= damage_taken
        message = f"{target.name} reflected the attack back at {self.name} for {damage_taken} damage!"
        whole_press_turn = 0
        half_press_turn = 0
    elif target.weakness[element] == "absorb":
        damage_taken = max(damage - target.vitality // 1.8, 1)
        whole_press_turn = 0
        half_press_turn = 0
        target.hp += int(damage_taken)
        if target.hp > target.max_hp:
            target.hp = target.max_hp
        damage_taken = int(damage_taken)
        message = f"{target.name} absorbed the attack for {damage_taken} health!"
    elif target.weakness[element] == "nullify":
        if half_press_turn >= 2:
            half_press_turn -= 2
        elif half_press_turn > 1 and whole_press_turn > 1:
            half_press_turn -= 1
            whole_press_turn -= 1
        else:
            whole_press_turn -= 2
        message = f"{target.name} took no damage!"
    else:
        if target.is_defending:
            damage = damage // 1.5
        if target.weakness[element] == "weak" and not target.is_defending:
            damage_taken = max(damage - target.vitality // 1.8 * 2, 1)
            message = f"Hit {target.name}'s weakness! "
            if not is_crit:
                if whole_press_turn > 0:
                    whole_press_turn -= 1
                    half_press_turn += 1
                else:
                    half_press_turn -= 1
        elif target.weakness[element] == "resist":
            damage_taken = max((damage - math.floor(target.vitality // 1.5)) // 2, 1)
        else:
            damage_taken = max(damage - math.floor(target.vitality // 1.5), 1)
        damage_taken = int(damage_taken)
        target.hp -= int(damage_taken)
        message += f"{target.name} took {damage_taken} damage!"
        target.shake_timer = 15
        if target.hp < 0:
            target.hp = 0
    return whole_press_turn, half_press_turn, message


def heal(self, target, power):
    health_restored = self.magic * power
    target.hp += health_restored
    if target.hp > target.max_hp:
        target.hp = target.max_hp
    return f"{target.name} restored {health_restored} health!"


# import monster data
with open("monsters.json", "r") as file:
    data = json.load(file)
monster_refs = {}
for monster_data in data["monsters"]:
    # Load sprite here
    sprite_filename = "assets/" + monster_data["name"] + ".png"  # Assuming sprite filename matches monster name
    sprite = pygame.image.load(sprite_filename).convert_alpha()
    sprite = pygame.transform.scale(sprite, (SCREEN_WIDTH // 4, SCREEN_HEIGHT * 2 // 3))

    monster_ref = monster.MonsterRef(
        name=monster_data["name"],
        max_hp=monster_data["attributes"]["max_hp"],
        max_mp=monster_data["attributes"]["max_mp"],
        strength=monster_data["attributes"]["strength"],
        magic=monster_data["attributes"]["magic"],
        vitality=monster_data["attributes"]["vitality"],
        agility=monster_data["attributes"]["agility"],
        luck=monster_data["attributes"]["luck"],
        moves=monster_data["attributes"]["moves"],
        weakness=monster_data["weakness"],
        sprite=sprite
    )
    monster_refs[monster_ref.name] = monster_ref

# import move data
with open("moves.json", "r") as file:
    data = json.load(file)
move_dict = {}
for move_data in data["moves"]:
    move = moves.Move(
        name=move_data["name"],
        type=move_data["attributes"]["type"],
        hp_cost=move_data["attributes"]["hp_cost"],
        mp_cost=move_data["attributes"]["mp_cost"],
        power=move_data["attributes"]["power"],
        critrate=move_data["attributes"]["critrate"],
        element=move_data["attributes"]["element"],
        target=move_data["attributes"]["target"]
    )
    move_dict[move.name] = move

# Define Characters and Enemies
characters = [
    monster.Monster(0, monster_refs["Hellpack"], 50),
    monster.Monster(1, monster_refs["Hellpack"], 12),
    monster.Monster(2, monster_refs["Black Unicorn"], 10),
    monster.Monster(3, monster_refs["Bathycanth"], 1)
]
enemies = [
    monster.Monster(0, monster_refs["Psycorvus"], 12),
    monster.Monster(1, monster_refs["Hellpack"], 12),
    monster.Monster(2, monster_refs["Psycorvus"], 12),
    monster.Monster(3, monster_refs["Hellpack"], 12)

]

# Define game states
PLAYER_TURN_START = 0
VICTORY_STATE = 1
DEFEAT_STATE = 2
SELECT_MOVE = 3
INSUFFICIENT_RESOURCES = 4
SELECT_ENEMY = 5
PLAYER_CALCULATE_ATTACK = 6
HEAL_TEXT = 7
ENEMY_DEFEAT = 8
PLAYER_CRITICAL_HIT = 9
PLAYER_DEAL_DAMAGE = 10
ENEMY_TURN_START = 11
DEAL_HEALING = 12
ENEMY_DEAL_DAMAGE = 13
ENEMY_TURN = 14
ENEMY_CALCULATE_DAMAGE = 15
ENEMY_CRITICAL_HIT = 16
ENEMY_HEAL_TEXT = 17
ENEMY_DEAL_HEALING = 18
LEVEL_UP = 19
ENEMY_DEFEAT_2 = 20

current_state = 0
whole_press_turn_count = 0
half_press_turn_count = 0
selected_option = 0
current_character = 0
selected_target = 0
selected_move = 0
attack_damage = 0
attack_message = ""
enemy_move = None
target_character = None
character = None
enemy_index = 0
enemy = enemies[0]
is_critical_hit = False
target_index = 0
current_enemy = None
current_message = False
enemies_to_hit = 0
characters_to_hit = 0
battle_count = 1
background_animation_timer = 0


def get_scaled_image(scale_factor):
    if scale_factor not in scaled_images_cache:
        scaled_image = pygame.transform.smoothscale(temple_image, (
            int(temple_image.get_width() * scale_factor),
            int(temple_image.get_height() * scale_factor)
        ))
        scaled_images_cache[scale_factor] = scaled_image
    return scaled_images_cache[scale_factor]


scaled_images_cache = {}
start_position = 10
end_position = 0
start_value = 1
end_value = 3.5
num_steps = 8  # Number of steps from start_value to end_value


# Game loop
running = True
while running:

    fpsClock.tick(fps)

    if background_animation_timer > 0:

        # Calculate the output using linear interpolation
        output = start_value + (end_value - start_value) * (
                    (background_animation_timer - start_position) / (end_position - start_position))

        # Ensure the output is clamped between start_value and end_value
        output = max(min(output, end_value), start_value)

        # Get the scaled temple image from cache
        scaled_temple_image = get_scaled_image(output)

        image_width, image_height = scaled_temple_image.get_size()

        # Calculate the position to draw the scaled temple image
        temple_x = (SCREEN_WIDTH - image_width) // 1.99
        temple_y = (SCREEN_HEIGHT - image_height) // 1.925

        # Draw the background and scaled temple images
        screen.blit(background_image, (0, 0))  # Draw the background
        screen.blit(scaled_temple_image, (temple_x, temple_y))  # Draw the scaled temple image
        screen.blit(shadow_image, (0, 0))

        background_animation_timer -= 1
    else:
        render_background()

    render_health_bars()
    render_press_turn_icons()
    SELECT_COLOR = pulsate_color()

    for enemy_sprite in enemies:
        screen.blit(enemy_sprite.sprite,
                    (SCREEN_WIDTH*3//64 + enemy_sprite.id * SCREEN_WIDTH*3.5//16 + enemy_sprite.sprite_x,
                     SCREEN_HEIGHT//5 + enemy_sprite.sprite_y))
        enemy_sprite.update_position()     # enemy movement animation

    if current_state == PLAYER_TURN_START:
        whole_press_turn_count = 0
        half_press_turn_count = 0
        if render_primary_text("-- Player's turn --"):
            for character in characters:
                character.is_defending = False
                if character.hp != 0:
                    whole_press_turn_count += 1
            current_state = SELECT_MOVE
            selected_option = 0
            current_character = 0
            enemies_to_hit = 0

    elif current_state == INSUFFICIENT_RESOURCES:
        if render_primary_text("Insufficient HP/MP!"):
            current_state = SELECT_MOVE
            selected_option = 0

    elif current_state == SELECT_MOVE:
        selected_action = None
        if whole_press_turn_count + half_press_turn_count > 0:
            character = characters[current_character]
            if character.hp == 0:
                current_character = (current_character + 1) % len(characters)
            else:
                render_primary_text(f"Select an attack for {character.name}", False)
                selected_option, check = choose_action(character, selected_option)
                if check:
                    selected_action = character.moves[selected_option]
                    move_hp_cost = int(move_dict.get(selected_action).hp_cost * character.max_hp)
                    # check if character has enough resources to use selected move
                    if move_hp_cost < character.hp and move_dict.get(selected_action).mp_cost < character.mp:
                        character.hp -= move_hp_cost
                        character.mp -= move_dict.get(selected_action).mp_cost
                        current_character = (current_character + 1) % len(characters)
                        current_state = SELECT_ENEMY
                        selected_move = move_dict.get(character.moves[selected_option])
                        if selected_move.type == "defend":
                            if half_press_turn_count > 0:
                                half_press_turn_count -= 1
                            else:
                                whole_press_turn_count -= 1
                                half_press_turn_count += 1

                        selected_option = 0
                        check = False
                    else:
                        current_state = INSUFFICIENT_RESOURCES
        else:
            current_state = ENEMY_TURN_START

    elif current_state == SELECT_ENEMY:
        if selected_move.type == "damage":
            enemies_to_hit = 0
            if selected_move.target == "enemy":
                render_primary_text("Select an target.", False)
                selected_option, check = choose_target(enemies, selected_option)
                if check:
                    enemy_index = selected_option
                    selected_option = 0
                    selected_target = enemies[enemy_index]
                    is_damage_calculated = False
                    attack_damage = 0
                    current_state = PLAYER_CALCULATE_ATTACK
            elif selected_move.target == "enemy_all":
                enemies_to_hit = len(enemies)
                selected_option = 0

                is_damage_calculated = False
                attack_damage = 0
                current_state = PLAYER_CALCULATE_ATTACK

        elif selected_move.type == "heal":
            selected_option, check = choose_target(characters, selected_option)
            if check:
                target_index = selected_option
                selected_option = 0
                selected_target = characters[target_index]
                current_state = HEAL_TEXT
        elif selected_move.type == "defend":
            if render_primary_text(f"{character.name} raises their guard."):
                character.is_defending = True
                current_state = SELECT_MOVE

    elif current_state == PLAYER_CALCULATE_ATTACK:
        if enemies_to_hit > 0:
            enemy_index = len(enemies) - enemies_to_hit
            selected_target = enemies[enemy_index]
            if render_primary_text(f"{character.name} attacks {enemies[enemy_index].name} with {selected_move.name}."):
                whole_press_turn_count, half_press_turn_count, attack_damage, is_critical_hit = calculate_damage(
                    character, selected_move, whole_press_turn_count, half_press_turn_count)
                if is_critical_hit:
                    current_state = PLAYER_CRITICAL_HIT
                else:
                    whole_press_turn_count, half_press_turn_count, attack_message = \
                        attack(character, selected_target, attack_damage, selected_move.element, whole_press_turn_count,
                               half_press_turn_count, is_critical_hit)

                    current_state = PLAYER_DEAL_DAMAGE
        elif render_primary_text(f"{character.name} attacks {enemies[enemy_index].name} with {selected_move.name}."):
            whole_press_turn_count, half_press_turn_count, attack_damage, is_critical_hit = calculate_damage(
                character, selected_move, whole_press_turn_count, half_press_turn_count,)
            if is_critical_hit:
                whole_press_turn_count, half_press_turn_count, attack_message = \
                    attack(character, selected_target, attack_damage, selected_move.element, whole_press_turn_count,
                           half_press_turn_count, is_critical_hit)
                attack_message = "Critical hit! " + attack_message
                current_state = PLAYER_DEAL_DAMAGE
            else:
                whole_press_turn_count, half_press_turn_count, attack_message = \
                    attack(character, selected_target, attack_damage, selected_move.element, whole_press_turn_count,
                           half_press_turn_count, is_critical_hit)

                current_state = PLAYER_DEAL_DAMAGE

    elif current_state == PLAYER_DEAL_DAMAGE:
        if render_primary_text(attack_message):
            if enemies[enemy_index].hp == 0:
                defeat_sound.play()
                enemies[enemy_index].fadeout = True
                current_state = ENEMY_DEFEAT
            elif enemies_to_hit > 1:
                enemies_to_hit -= 1
                is_damage_calculated = False
                attack_damage = 0
                current_state = PLAYER_CALCULATE_ATTACK
            else:
                current_state = SELECT_MOVE

    elif current_state == LEVEL_UP:
        if render_primary_text(f"{i.name} reached level {i.level + 1}! "):
            i.level_up(monster_refs[i.name])
            current_state = ENEMY_DEFEAT_2

    elif current_state == ENEMY_DEFEAT:
        if render_primary_text(f"{enemies[enemy_index].name} has been defeated."):
            alive_characters = [character for character in characters if character.hp > 0]
            for i in alive_characters:
                i.exp += int(enemies[enemy_index].exp ** 0.8 // len(alive_characters))
            current_state = ENEMY_DEFEAT_2

    elif current_state == ENEMY_DEFEAT_2:
        for i in alive_characters:
            if i.exp > (i.level+1) ** 3:
                current_state = LEVEL_UP
                break
        if current_state != LEVEL_UP:
            enemies.pop(enemy_index)
            if not enemies:
                whole_press_turn_count = 0
                half_press_turn_count = 0
                current_state = VICTORY_STATE
            elif enemies_to_hit > 1:
                enemies_to_hit -= 1
                is_damage_calculated = False
                attack_damage = 0
                current_state = PLAYER_CALCULATE_ATTACK
            else:
                current_state = SELECT_MOVE

    elif current_state == HEAL_TEXT:
        if render_primary_text(f"{character.name} heals {characters[target_index].name} with {selected_move.name}."):
            heal_sound.play()
            current_state = DEAL_HEALING

    elif current_state == DEAL_HEALING:
        attack_message = heal(character, characters[target_index], selected_move.power)
        if render_primary_text(attack_message):
            current_state = SELECT_MOVE

    elif current_state == ENEMY_TURN_START:
        if render_primary_text("-- Enemy Turn --"):
            current_state = ENEMY_TURN
            whole_press_turn_count = len(enemies)
            enemy_move = None
            target_character = None
            characters_to_hit = 0
            current_enemy = 0

    elif current_state == ENEMY_TURN:
        if whole_press_turn_count > 0 or half_press_turn_count > 0:
            enemy = enemies[current_enemy]
            if enemy_move is None:
                enemy_move = random.choice([move for move in enemy.moves[:-1]])  # enemy selects random move sans Guard
                enemy_move = move_dict.get(enemy_move)
            if enemy_move.type == "damage":
                if enemy_move.target == "enemy":
                    target_character = random.choice([character for character in characters if character.hp > 0])
                    current_state = ENEMY_CALCULATE_DAMAGE
                elif enemy_move.target == "enemy_all":
                    alive_characters = [character for character in characters if character.hp > 0]
                    characters_to_hit = len(alive_characters)
                    target_character = characters[len(alive_characters) - characters_to_hit]
                    current_state = ENEMY_CALCULATE_DAMAGE
            elif enemy_move.type == "heal":
                characters_needing_healing = [character for character in enemies if character.hp < character.max_hp]
                if characters_needing_healing:
                    target_character = random.choice(characters_needing_healing)
                    current_state = ENEMY_HEAL_TEXT
                else:
                    enemy_move = None
        else:
            current_state = PLAYER_TURN_START

    elif current_state == ENEMY_CALCULATE_DAMAGE:
        if render_primary_text(f"{enemy.name} attacks {target_character.name} with {enemy_move.name}."):
            whole_press_turn_count, half_press_turn_count, attack_damage, is_critical_hit = \
                calculate_damage(enemy, enemy_move, whole_press_turn_count, half_press_turn_count,)
            if is_critical_hit:
                current_state = ENEMY_CRITICAL_HIT
            else:
                whole_press_turn_count, half_press_turn_count, attack_message = attack(
                    enemy, target_character, attack_damage, enemy_move.element, whole_press_turn_count,
                    half_press_turn_count, is_critical_hit)
                current_state = ENEMY_DEAL_DAMAGE

    elif current_state == ENEMY_CRITICAL_HIT:
        if render_primary_text("Critical Hit!"):
            whole_press_turn_count, half_press_turn_count, attack_message = \
                attack(character, target_character, attack_damage, enemy_move.element, whole_press_turn_count,
                       half_press_turn_count, is_critical_hit)
            current_state = ENEMY_DEAL_DAMAGE

    elif current_state == ENEMY_DEAL_DAMAGE:
        if characters_to_hit > 1:
            if render_primary_text(attack_message):
                characters_to_hit -= 1
                target_character = characters[len(alive_characters) - characters_to_hit]
                current_state = ENEMY_CALCULATE_DAMAGE
            if all(character.hp <= 0 for character in characters):
                render_primary_text("Defeated!", False)
                current_state = DEFEAT_STATE
        elif render_primary_text(attack_message):
            if whole_press_turn_count > 0:
                whole_press_turn_count -= 1
            else:
                half_press_turn_count -= 1
            current_enemy = (current_enemy + 1) % len(enemies)
            current_state = ENEMY_TURN
        if all(character.hp <= 0 for character in characters):
            render_primary_text("Defeated!", False)
            current_state = DEFEAT_STATE

    elif current_state == ENEMY_HEAL_TEXT:
        if render_primary_text(f"{enemy.name} heals {enemies[target_index].name} with {enemy_move.name}."):
            current_state = ENEMY_DEAL_HEALING

    elif current_state == ENEMY_DEAL_HEALING:
        attack_message = heal(enemy, enemies[target_index], enemy_move.power)
        if render_primary_text(attack_message):
            if whole_press_turn_count > 0:
                whole_press_turn_count -= 1
            else:
                half_press_turn_count -= 1
            current_enemy = (current_enemy + 1) % len(enemies)
            current_state = ENEMY_TURN

    elif current_state == VICTORY_STATE:
        if render_primary_text("You win!"):
            enemies = [monster.Monster(random.randint(0, 3), monster_refs["Hellpack"], 10 + battle_count)]
            battle_count += 1
            background_animation_timer = num_steps
            current_state = PLAYER_TURN_START

    elif current_state == DEFEAT_STATE:
        render_primary_text("Game Over")
        pygame.mixer.music.stop()
        pass

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.flip()

pygame.quit()
sys.exit()
