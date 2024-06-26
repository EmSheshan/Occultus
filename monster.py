import math
from math import ceil
import pygame
import roman


class MonsterRef:
    def __init__(self, name, max_hp, max_mp, strength, magic, vitality, agility, luck, moves, weakness, sprite):
        self.name = name
        self.max_hp = max_hp
        self.max_mp = max_mp
        self.strength = strength
        self.magic = magic
        self.vitality = vitality
        self.agility = agility
        self.luck = luck
        moves.append('Guard')
        self.moves = moves
        self.weakness = weakness
        self.sprite = sprite


class Monster:
    def __init__(self, m_id, monster_ref, level):
        self.id = m_id
        r = roman.toRoman(m_id + 1)
        self.name = monster_ref.name + " " + r.lower()
        self.level = level
        self.max_hp = ceil(monster_ref.max_hp * level / 25)
        self.hp = self.max_hp
        self.max_mp = ceil(monster_ref.max_mp * level / 25)
        self.mp = self.max_mp
        self.strength = ceil(monster_ref.strength * level / 25)
        self.magic = ceil(monster_ref.magic * level / 25)
        self.vitality = ceil(monster_ref.vitality * level / 25)
        self.agility = ceil(monster_ref.agility * level / 25)
        self.luck = ceil(monster_ref.luck * level / 25)
        self.moves = monster_ref.moves
        self.weakness = monster_ref.weakness
        self.is_defending = False

        self.original_sprite = monster_ref.sprite
        self.tinted_sprite = self.original_sprite.copy()  # Create a copy of the original sprite
        self.tinted_sprite.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)  # Tint the copy
        self.sprite = self.original_sprite
        self.shake_timer = 0
        self.sprite_y = 0  # Initial vertical position
        self.sprite_x = 0

    def update_position(self):
        # Slight vertical bobbing motion
        self.sprite_y = self.sprite_y + 0.2 * math.sin(pygame.time.get_ticks() * 0.002)

        # Check if the enemy is currently shaking
        if self.shake_timer == 0:
            self.sprite_x = 0
            self.sprite = self.original_sprite
        elif self.shake_timer > 0:
            # Calculate the displacement based on a sine wave function
            displacement = 12 * math.sin(self.shake_timer * 2 * math.pi / 12)
            # Update the x-coordinate based on the displacement
            self.sprite_x += displacement
            # Decrease the shake timer
            self.shake_timer -= 1
            self.sprite = self.tinted_sprite


