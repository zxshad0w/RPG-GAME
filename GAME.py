"""
МЕГА RPG ИГРА "ДРАКОНОВОЕ ЗАКЛИНАНИЕ" - УЛУЧШЕННАЯ ВЕРСИЯ 2.0.3
Исправления: увеличены враги на локациях, добавлен функционал для оружия, оптимизация кода
"""

import random
import time
import json
import os
import copy
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
import sys

class Color:
    """Класс для цветного вывода в терминале"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class CharacterClass(Enum):
    """Классы персонажей"""
    WARRIOR = "Воин"
    MAGE = "Маг"
    ARCHER = "Лучник"
    ROGUE = "Разбойник"

class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "Оружие"
    ARMOR = "Броня"
    HELMET = "Шлем"
    GLOVES = "Перчатки"
    BOOTS = "Сапоги"
    RING = "Кольцо"
    AMULET = "Амулет"
    POTION = "Зелье"
    SCROLL = "Свиток"
    QUEST = "Квестовый предмет"
    MATERIAL = "Материал"
    KEY = "Ключ"

class QuestStatus(Enum):
    """Статусы квестов"""
    NOT_STARTED = "Не начат"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Завершен"
    FAILED = "Провален"

class LocationType(Enum):
    """Типы локаций"""
    TOWN = "Город"
    FOREST = "Лес"
    DUNGEON = "Подземелье"
    MOUNTAIN = "Горы"
    CAVE = "Пещера"
    RUINS = "Руины"
    SWAMP = "Болото"
    BEACH = "Пляж"
    BORDELLO = "Бордель"

class EnemyType(Enum):
    """Типы врагов"""
    GOBLIN = "Гоблин"
    ORC = "Орк"
    WOLF = "Волк"
    SKELETON = "Скелет"
    TROLL = "Тролль"
    DRAGON = "Дракон"
    BANDIT = "Бандит"
    SPIDER = "Паук"
    WITCH = "Ведьма"
    NECROMANCER = "Некромант"
    SLIME = "Слизень"  # Добавим для достижений

class Difficulty(Enum):
    """Уровни сложности"""
    EASY = "Легкий"
    NORMAL = "Нормальный"
    HARD = "Сложный"
    INSANE = "Безумный"

class Card:
    """Класс карты для блэкджека"""
    def __init__(self, rank: str, suit: str, value: int):
        self.rank = rank
        self.suit = suit
        self.value = value
    
    def __str__(self):
        suits_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }
        return f"{self.rank}{suits_symbols.get(self.suit, self.suit[0])}"

class Deck:
    """Колода карт для блэкджека"""
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """Сброс и перетасовка колоды"""
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        
        self.cards = []
        for suit in suits:
            for rank, value in ranks.items():
                self.cards.append(Card(rank, suit, value))
        
        random.shuffle(self.cards)
    
    def draw(self):
        """Взять карту из колоды"""
        if not self.cards:
            self.reset()
        return self.cards.pop()

class Item:
    """Класс предмета с улучшениями"""
    def __init__(self, name: str, item_type: ItemType, value: int = 0, 
                damage: int = 0, defense: int = 0, health: int = 0,
                mana: int = 0, description: str = "", durability: int = 100,
                required_level: int = 1, armor_slot: str = None,
                character_classes: List[CharacterClass] = None,
                special_effect: str = None):
        self.id = random.randint(1000, 9999)
        self.name = name
        self.item_type = item_type
        self.value = value
        self.damage = damage
        self.defense = defense
        self.health = health
        self.mana = mana
        self.description = description
        self.durability = durability
        self.max_durability = durability
        self.required_level = required_level
        self.armor_slot = armor_slot
        self.special_effect = special_effect  # Специальный эффект оружия
        self.rarity = self.calculate_rarity()
        self.character_classes = character_classes or [CharacterClass.WARRIOR, CharacterClass.MAGE, CharacterClass.ARCHER, CharacterClass.ROGUE]
    
    def is_suitable_for_class(self, character_class: CharacterClass) -> bool:
        """Проверка, подходит ли предмет для класса персонажа"""
        return character_class in self.character_classes
    
    def calculate_rarity(self):
        """Расчет редкости предмета на основе характеристик"""
        total_power = (self.damage * 2) + (self.defense * 3) + self.health + self.mana
        
        if total_power >= 150:
            return "Легендарный"
        elif total_power >= 100:
            return "Эпический"
        elif total_power >= 60:
            return "Редкий"
        elif total_power >= 30:
            return "Необычный"
        else:
            return "Обычный"

    def get_colored_name(self) -> str:
        """Возвращает цветное имя в зависимости от редкости"""
        colors = {
            "Обычный": Color.WHITE,
            "Необычный": Color.GREEN,
            "Редкий": Color.BLUE,
            "Эпический": Color.PURPLE,
            "Легендарный": Color.YELLOW
        }
        color = colors.get(self.rarity, Color.WHITE)
        durability_color = Color.GREEN if self.durability > self.max_durability * 0.5 else Color.YELLOW if self.durability > self.max_durability * 0.2 else Color.RED
        durability_text = f" [{durability_color}{self.durability}/{self.max_durability}{Color.END}]" if self.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.HELMET, ItemType.GLOVES, ItemType.BOOTS] else ""
        return f"{color}{self.name}{Color.END}{durability_text}"
    
    def degrade(self, amount: int = 1):
        """Уменьшение прочности предмета"""
        if self.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.HELMET, ItemType.GLOVES, ItemType.BOOTS]:
            self.durability = max(0, self.durability - amount)
            return self.durability <= 0
        return False
    
    def repair(self, amount: int = 100):
        """Ремонт предмета"""
        if self.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.HELMET, ItemType.GLOVES, ItemType.BOOTS]:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def copy(self):
        """Создание копии предмета"""
        new_item = Item(
            name=self.name,
            item_type=self.item_type,
            value=self.value,
            damage=self.damage,
            defense=self.defense,
            health=self.health,
            mana=self.mana,
            description=self.description,
            durability=self.durability,
            required_level=self.required_level,
            armor_slot=self.armor_slot,
            character_classes=self.character_classes,
            special_effect=self.special_effect
        )
        new_item.id = self.id
        new_item.rarity = self.rarity
        return new_item
    
    def is_equippable(self, player_level: int) -> bool:
        """Проверка, может ли игрок экипировать предмет"""
        return player_level >= self.required_level
    
    def apply_special_effect(self, player, enemy=None) -> Tuple[int, str]:
        """Применение специального эффекта оружия"""
        if not self.special_effect:
            return 0, ""
        
        effect = self.special_effect
        if effect == "fire_damage":
            # Дополнительный огненный урон
            bonus_damage = random.randint(3, 8)
            return bonus_damage, f"{Color.RED}Огненный урон! +{bonus_damage}{Color.END}"
        
        elif effect == "mana_steal":
            # Кража маны
            mana_steal = random.randint(5, 15)
            if enemy and hasattr(enemy, 'type') and enemy.type == EnemyType.NECROMANCER:
                # Некроманты дают больше маны
                mana_steal *= 2
            player.mana = min(player.max_mana, player.mana + mana_steal)
            return 0, f"{Color.BLUE}Кража маны! +{mana_steal} маны{Color.END}"
        
        elif effect == "critical_chance":
            # Увеличенный шанс крита
            player.stats["luck"] += 3  # Временный бонус
            return 0, f"{Color.YELLOW}Увеличен шанс критического удара!{Color.END}"
        
        elif effect == "poison":
            # Ядовитый урон
            poison_damage = random.randint(2, 5)
            return poison_damage, f"{Color.GREEN}Ядовитый урон! +{poison_damage} в течение 3 ходов{Color.END}"
        
        elif effect == "life_steal":
            # Кража здоровья
            life_steal = random.randint(3, 10)
            player.heal(life_steal)
            return 0, f"{Color.RED}Кража здоровья! +{life_steal} HP{Color.END}"
        
        elif effect == "stun_chance":
            # Шанс оглушения
            stun_chance = random.random()
            if stun_chance < 0.2:  # 20% шанс оглушить
                return 0, f"{Color.PURPLE}Противник оглушен на 1 ход!{Color.END}"
        
        elif effect == "armor_penetration":
            # Пробивание брони
            return 5, f"{Color.CYAN}Пробитие брони! Игнорирует 5 защиты{Color.END}"
        
        return 0, ""

class Enemy:
    """Класс врага с улучшениями"""
    def __init__(self, enemy_type: EnemyType, level: int = 1, difficulty: Difficulty = Difficulty.NORMAL):
        self.type = enemy_type
        self.level = level
        self.name = f"{enemy_type.value} Ур.{level}"
        self.difficulty = difficulty
        
        # Базовые характеристики в зависимости от типа
        base_stats = {
            EnemyType.GOBLIN: {"health": 30, "damage": 5, "defense": 2, "xp": 30, "gold": (20, 25)},
            EnemyType.ORC: {"health": 40, "damage": 8, "defense": 5, "xp": 30, "gold": (25, 30)},
            EnemyType.WOLF: {"health": 20, "damage": 6, "defense": 1, "xp": 15, "gold": (10, 20)},
            EnemyType.SKELETON: {"health": 30, "damage": 7, "defense": 3, "xp": 15, "gold": (10, 15)},
            EnemyType.TROLL: {"health": 55, "damage": 12, "defense": 8, "xp": 30, "gold": (10, 25)},
            EnemyType.DRAGON: {"health": 200, "damage": 25, "defense": 15, "xp": 150, "gold": (50, 100)},
            EnemyType.BANDIT: {"health": 35, "damage": 6, "defense": 4, "xp": 20, "gold": (20, 25)},
            EnemyType.SPIDER: {"health": 15, "damage": 4, "defense": 1, "xp": 20, "gold": (10, 15)},
            EnemyType.WITCH: {"health": 40, "damage": 9, "defense": 3, "xp": 30, "gold": (15, 30)},
            EnemyType.NECROMANCER: {"health": 60, "damage": 11, "defense": 6, "xp": 40, "gold": (20, 40)},
            EnemyType.SLIME: {"health": 25, "damage": 3, "defense": 1, "xp": 20, "gold": (10, 20)}
        }
        
        stats = base_stats.get(enemy_type, base_stats[EnemyType.GOBLIN])
        
        # Масштабирование по уровню
        scale = 1 + (level - 1) * 0.3
        
        # Модификатор сложности
        difficulty_mult = {
            Difficulty.EASY: 0.8,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.3,
            Difficulty.INSANE: 1.8
        }.get(difficulty, 1.0)
        
        self.max_health = int(stats["health"] * scale * difficulty_mult)
        self.health = self.max_health
        self.damage = int(stats["damage"] * scale * difficulty_mult)
        self.defense = int(stats["defense"] * scale * difficulty_mult)
        self.xp_reward = int(stats["xp"] * scale * difficulty_mult)
        
        # Награда золотом с учетом сложности
        gold_min, gold_max = stats["gold"]
        gold_min = int(gold_min * scale * difficulty_mult)
        gold_max = int(gold_max * scale * difficulty_mult)
        self.gold_reward = random.randint(gold_min, gold_max)
        
        # Шанс выпадения лута в зависимости от сложности
        self.loot_chance = 0.3 * difficulty_mult
        
        # Особые способности врагов
        self.special_abilities = self.get_special_abilities()
    
    def get_special_abilities(self) -> List[str]:
        """Получение особых способностей врага"""
        abilities = []
        
        if self.type == EnemyType.DRAGON:
            abilities.append("Огненное дыхание")
        elif self.type == EnemyType.WITCH:
            abilities.append("Магический щит")
        elif self.type == EnemyType.NECROMANCER:
            abilities.append("Воскрешение скелетов")
        elif self.type == EnemyType.SPIDER:
            abilities.append("Ядовитый укус")
        elif self.type == EnemyType.SLIME:
            abilities.append("Кислотная атака")
        
        return abilities
    
    def use_special_ability(self) -> Tuple[int, str]:
        """Использование особой способности"""
        if not self.special_abilities:
            return 0, ""
        
        ability = random.choice(self.special_abilities)
        
        if ability == "Огненное дыхание":
            damage = int(self.damage * 1.5)
            return damage, f"{self.name} использует Огненное дыхание!"
        elif ability == "Магический щит":
            self.defense += 5
            return 0, f"{self.name} использует Магический щит! (+5 к защите)"
        elif ability == "Ядовитый укус":
            damage = int(self.damage * 1.2)
            return damage, f"{self.name} использует Ядовитый укус! (яд)"
        elif ability == "Кислотная атака":
            damage = int(self.damage * 0.8)
            armor_reduction = 2
            return damage, f"{self.name} использует Кислотную атаку! (-{armor_reduction} защиты)"
        elif ability == "Воскрешение скелетов":
            # Здесь можно было бы добавить логику воскрешения
            return 0, f"{self.name} пытается воскресить скелетов!"
        
        return 0, ""

class Location:
    """Класс локации с улучшениями"""
    def __init__(self, name: str, loc_type: LocationType, level_range: Tuple[int, int],
                 description: str, connections: List[str] = None, 
                 has_shop: bool = False, has_tavern: bool = False,
                 has_bordello: bool = False, special_event_chance: float = 0.1):
        self.name = name
        self.type = loc_type
        self.level_range = level_range
        self.description = description
        self.connections = connections or []
        self.has_shop = has_shop
        self.has_tavern = has_tavern
        self.has_bordello = has_bordello
        self.special_event_chance = special_event_chance
        self.enemies = []
        self.quests = []
        self.discovered = False
        self.cleared = False
        self.respawn_timer = 0
        
        # Генерация врагов для локации - ИСПРАВЛЕНО: увеличение количества врагов
        self.generate_enemies()
    
    def generate_enemies(self):
        """Генерация врагов для локации - ИСПРАВЛЕНО: теперь 5-10 врагов"""
        enemy_types = list(EnemyType)
        # Генерируем от 5 до 10 врагов вместо 2-8
        num_enemies = random.randint(5, 10)
        
        for _ in range(num_enemies):
            enemy_type = random.choice(enemy_types)
            level = random.randint(self.level_range[0], self.level_range[1])
            self.enemies.append(Enemy(enemy_type, level))
    
    def should_respawn(self) -> bool:
        """Проверка, должны ли возродиться враги"""
        if not self.enemies and not self.cleared:
            self.respawn_timer += 1
            if self.respawn_timer >= 3:  # Через 3 посещения
                self.generate_enemies()
                self.respawn_timer = 0
                return True
        return False
    
    def clear_enemies(self):
        """Очистка локации от врагов"""
        self.enemies.clear()
        self.cleared = True
    
    def add_special_event(self):
        """Добавление специального события"""
        events = [
            "Вы нашли заброшенный алтарь",
            "Вы обнаружили тайный проход",
            "Вы наткнулись на странные символы",
            "Вы чувствуете магическую энергию",
            "Вы слышите странные звуки",
            "Вы нашли древнюю надпись",
            "Вы чувствуете дрожь земли",
            "Вы видите странное свечение"
        ]
        return random.choice(events)

class Quest:
    """Класс квеста с улучшениями"""
    def __init__(self, name: str, description: str, location: str,
                 reward_xp: int, reward_gold: int, required_level: int = 1,
                 quest_type: str = "main", time_limit: int = 0):
        self.id = random.randint(100, 999)
        self.name = name
        self.description = description
        self.location = location
        self.status = QuestStatus.NOT_STARTED
        self.reward_xp = reward_xp
        self.reward_gold = reward_gold
        self.required_level = required_level
        self.quest_type = quest_type
        self.time_limit = time_limit
        self.start_time = None
        self.objectives = {}
        self.completed_objectives = {}
        self.reward_items = []
        
    def add_objective(self, objective: str, target: str, count: int):
        """Добавление цели квеста"""
        self.objectives[objective] = {"target": target, "count": count, "current": 0}
        
    def add_reward_item(self, item: Item):
        """Добавление предмета в награду"""
        self.reward_items.append(item)
        
    def start(self):
        """Начало квеста"""
        self.status = QuestStatus.IN_PROGRESS
        self.start_time = datetime.now()
        
    def update_objective(self, objective: str, amount: int = 1) -> bool:
        """Обновление прогресса цели"""
        if objective in self.objectives:
            self.objectives[objective]["current"] += amount
            if self.objectives[objective]["current"] >= self.objectives[objective]["count"]:
                self.completed_objectives[objective] = True
                
                if all(obj in self.completed_objectives for obj in self.objectives):
                    self.status = QuestStatus.COMPLETED
                    return True
            return False
        return False
    
    def check_time_limit(self) -> bool:
        """Проверка временного лимита"""
        if self.time_limit > 0 and self.start_time:
            elapsed = (datetime.now() - self.start_time).seconds / 60
            if elapsed > self.time_limit:
                self.status = QuestStatus.FAILED
                return True
        return False

class Achievement:
    """Класс достижения"""
    def __init__(self, name: str, description: str, condition: str, 
                 target_value: int, reward_xp: int = 0, reward_gold: int = 0):
        self.name = name
        self.description = description
        self.condition = condition
        self.target_value = target_value
        self.reward_xp = reward_xp
        self.reward_gold = reward_gold
        self.current_value = 0
        self.completed = False
        self.completion_date = None
        
    def update(self, value: int = 1) -> bool:
        """Обновление прогресса достижения"""
        self.current_value += value
        if self.current_value >= self.target_value and not self.completed:
            self.completed = True
            self.completion_date = datetime.now()
            return True
        return False

class BordelloGirl:
    """Класс девушки из борделя"""
    def __init__(self, name: str, specialty: str, price: int, description: str):
        self.name = name
        self.specialty = specialty
        self.price = price
        self.description = description
        self.available = True
        self.stamina = 100
    
    def provide_service(self) -> Tuple[str, Dict[str, int]]:
        """Оказание услуги"""
        if not self.available:
            return "Девушка устала, приходите позже", {}
        
        self.stamina -= 20
        if self.stamina <= 0:
            self.available = False
            self.stamina = 0
        
        effects = {}
        
        if self.specialty == "Массаж":
            effects = {"health": 30, "stamina_recovery": 15}
            result = f"{self.name} делает вам расслабляющий массаж. Вы чувствуете прилив сил."
        elif self.specialty == "Танцы":
            effects = {"morale": 20, "gold_bonus": 10}
            result = f"{self.name} исполняет для вас зажигательный танец. Ваше настроение улучшается."
        elif self.specialty == "Беседа":
            effects = {"xp_bonus": 15, "quest_hint": True}
            result = f"{self.name} ведет с вами умную беседу. Вы узнаете полезную информацию."
        elif self.specialty == "Особое внимание":
            effects = {"health": 50, "max_health_bonus": 10, "morale": 30}
            result = f"{self.name} оказывает вам особое внимание. Вы чувствуете себя прекрасно."
        else:
            effects = {"health": 20, "morale": 10}
            result = f"{self.name} проводит с вами время."
        
        return result, effects
    
    def rest(self):
        """Отдых девушки"""
        self.stamina += 40
        if self.stamina >= 100:
            self.stamina = 100
            self.available = True

class Player:
    """Класс игрока с улучшениями"""
    def __init__(self, name: str, difficulty: Difficulty = Difficulty.NORMAL):
        self.name = name
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.max_health = 100
        self.health = 100
        self.max_mana = 50
        self.mana = 50
        self.gold = 50
        self.character_class = None
        self.skills = {}
        self.inventory = []
        self.equipped = {
            "weapon": None,
            "armor": None,
            "helmet": None,
            "gloves": None,
            "boots": None,
            "ring": None,
            "amulet": None
        }
        self.location = "Стартовая деревня"
        self.quests = []
        self.killed_enemies = {}
        self.play_time = 0
        self.save_slot = 1
        self.difficulty = difficulty
        self.achievements = []
        self.daily_quests = []
        self.last_login = datetime.now()
        self.active_effects = {}  # Активные эффекты от предметов
        
        # Статистика
        self.stats = {
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
            "constitution": 10,
            "luck": 5
        }
        
        # Новые характеристики
        self.morale = 100
        self.stamina = 100
        
        # Модификатор сложности
        self.difficulty_mult = {
            Difficulty.EASY: 1.2,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 0.8,
            Difficulty.INSANE: 0.6
        }.get(difficulty, 1.0)
        
        # Инициализация достижений
        self.initialize_achievements()
    
    def initialize_achievements(self):
        """Инициализация достижений"""
        self.achievements = [
            Achievement("Новичок", "Достигнуть 5 уровня", "level_up", 5, 100, 50),
            Achievement("Охотник", "Убить 50 врагов", "kill_enemy", 50, 200, 100),
            Achievement("Искатель приключений", "Завершить 10 квестов", "complete_quest", 10, 300, 150),
            Achievement("Богач", "Накопить 1000 золота", "collect_gold", 1000, 150, 200),
            Achievement("Мастер", "Достигнуть 20 уровня", "level_up", 20, 500, 300),
            Achievement("Слизнеборец", "Убить 10 слизней", "kill_slime", 10, 50, 25),
            Achievement("Драконоборец", "Победить дракона", "kill_dragon", 1, 1000, 500),
            Achievement("Коллекционер", "Собрать 50 предметов", "collect_item", 50, 200, 100),
            Achievement("Путешественник", "Посетить все локации", "visit_location", 10, 300, 150),
            Achievement("Легенда", "Завершить игру", "complete_game", 1, 1000, 1000)
        ]
    
    def set_class(self, char_class: CharacterClass):
        """Установка класса персонажа"""
        self.character_class = char_class
        
        class_bonuses = {
            CharacterClass.WARRIOR: {"strength": 7, "constitution": 5, "health": 20},
            CharacterClass.MAGE: {"intelligence": 10, "max_mana": 30, "mana": 50},
            CharacterClass.ARCHER: {"dexterity": 9, "strength": 4, "luck": 3},
            CharacterClass.ROGUE: {"dexterity": 7, "strength": 4, "intelligence": 4, "luck": 5}
        }
        
        bonuses = class_bonuses.get(char_class, {})
        for stat, value in bonuses.items():
            if stat == "mana":
                self.max_mana += value
                self.mana = self.max_mana
            elif stat == "health":
                self.max_health += value
                self.health = self.max_health
            elif stat == "max_mana":
                self.max_mana += value
                self.mana = self.max_mana
            else:
                self.stats[stat] += value
        
        self.update_derived_stats()
    
    def update_derived_stats(self):
        """Обновление производных характеристик"""
        self.max_health = 100 + self.stats["constitution"] * 5 + (self.level * 2)
        self.max_mana = 50 + self.stats["intelligence"] * 3 + (self.level * 1)
        
        if self.health > self.max_health:
            self.health = self.max_health
        if self.mana > self.max_mana:
            self.mana = self.max_mana
    
    def attack(self, enemy=None) -> Tuple[int, str]:
        """Атака игрока - ДОБАВЛЕН ФУНКЦИОНАЛ СПЕЦИАЛЬНЫХ ЭФФЕКТОВ ОРУЖИЯ"""
        base_damage = self.stats["strength"] // 2
        
        if self.character_class == CharacterClass.MAGE:
            base_damage += self.stats["intelligence"] // 3
        
        special_damage = 0
        special_message = ""
        
        if self.equipped["weapon"]:
            weapon = self.equipped["weapon"]
            base_damage += weapon.damage
            
            # Применение специального эффекта оружия
            if weapon.special_effect and enemy:
                effect_damage, effect_message = weapon.apply_special_effect(self, enemy)
                special_damage += effect_damage
                if effect_message:
                    special_message = effect_message
            
            weapon.degrade()
        
        # Критический удар
        crit_chance = (self.stats["dexterity"] + self.stats["luck"]) / 200
        is_critical = random.random() < crit_chance
        
        miss_chance = max(0, 0.05 - (self.stats["dexterity"] / 500))
        is_miss = random.random() < miss_chance
        
        if is_miss:
            return 0, f"{self.name} промахивается!"
        
        damage = base_damage + special_damage
        message = f"{self.name} атакует"
        
        if is_critical:
            damage = int(damage * (1.5 + (self.stats["luck"] / 100)))
            message += f" {Color.RED}КРИТИЧЕСКИ{Color.END}!"
        else:
            damage = random.randint(int(damage * 0.8), int(damage * 1.2))
        
        damage = int(damage * self.difficulty_mult)
        
        if special_message:
            message += f" {special_message}"
        
        return damage, message
    
    def take_damage(self, damage: int) -> bool:
        """Получение урона"""
        defense = self.stats["constitution"] // 3
        
        for slot in ["armor", "helmet", "gloves", "boots"]:
            if self.equipped[slot]:
                defense += self.equipped[slot].defense
                self.equipped[slot].degrade()
        
        dodge_chance = self.stats["dexterity"] / 300
        is_dodged = random.random() < dodge_chance
        
        if is_dodged:
            return False
        
        actual_damage = max(1, damage - defense)
        actual_damage = int(actual_damage / self.difficulty_mult)
        
        self.health -= actual_damage
        
        return self.health <= 0
    
    def heal(self, amount: int):
        """Лечение игрока"""
        self.health = min(self.max_health, self.health + amount)
    
    def restore_mana(self, amount: int):
        """Восстановление маны"""
        self.mana = min(self.max_mana, self.mana + amount)
    
    def gain_xp(self, amount: int) -> bool:
        """Получение опыта"""
        actual_amount = int(amount * self.difficulty_mult)
        self.xp += actual_amount
        
        self.check_achievement("level_up", 0)
        
        if self.xp >= self.xp_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.4)
        
        self.stats["strength"] += 2
        self.stats["dexterity"] += 2
        self.stats["intelligence"] += 2
        self.stats["constitution"] += 2
        self.stats["luck"] += 1
        
        class_bonus_stats = {
            CharacterClass.WARRIOR: {"strength": 3, "constitution": 2},
            CharacterClass.MAGE: {"intelligence": 3},
            CharacterClass.ARCHER: {"dexterity": 3, "strength": 1},
            CharacterClass.ROGUE: {"dexterity": 2, "luck": 2}
        }
        
        bonuses = class_bonus_stats.get(self.character_class, {})
        for stat, value in bonuses.items():
            if stat == "max_mana":
                self.max_mana += value
            else:
                self.stats[stat] += value
        
        self.update_derived_stats()
        self.health = self.max_health
        self.mana = self.max_mana
        
        print(f"{Color.YELLOW}Поздравляем! Вы достигли {self.level} уровня!{Color.END}")
        print(f"Здоровье: {self.health}/{self.max_health}")
        print(f"Мана: {self.mana}/{self.max_mana}")
        
        for achievement in self.achievements:
            if achievement.condition == "level_up":
                achievement.update()
    
    def add_item(self, item: Item):
        """Добавление предмета в инвентарь"""
        if len(self.inventory) < 40:
            self.inventory.append(item)
            self.check_achievement("collect_item", 1)
        else:
            print(f"{Color.RED}Инвентарь полон!{Color.END}")
    
    def remove_item(self, item: Item) -> bool:
        """Удаление предмета из инвентаря"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def equip_item(self, item: Item) -> bool:
        """Экипировка предмета"""
        if item not in self.inventory:
            return False
        
        if not item.is_equippable(self.level):
            print(f"{Color.RED}Ваш уровень слишком низок для этого предмета!{Color.END}")
            return False
        
        slot_map = {
            ItemType.WEAPON: "weapon",
            ItemType.ARMOR: "armor",
            ItemType.HELMET: "helmet",
            ItemType.GLOVES: "gloves",
            ItemType.BOOTS: "boots",
            ItemType.RING: "ring",
            ItemType.AMULET: "amulet"
        }
        
        slot = slot_map.get(item.item_type)
        
        if item.item_type == ItemType.ARMOR and item.armor_slot:
            slot = item.armor_slot
        
        if not slot:
            return False
        
        if self.equipped[slot]:
            self.inventory.append(self.equipped[slot])
        
        self.equipped[slot] = item
        self.inventory.remove(item)
        
        return True
    
    def unequip_item(self, slot: str) -> bool:
        """Снятие предмета"""
        if self.equipped[slot]:
            self.inventory.append(self.equipped[slot])
            self.equipped[slot] = None
            return True
        return False
    
    def get_stat_bonus(self, stat: str) -> int:
        """Получение бонуса от статов"""
        return self.stats[stat] // 10
    
    def check_achievement(self, condition: str, value: int = 1):
        """Проверка и обновление достижений"""
        for achievement in self.achievements:
            if achievement.condition == condition and not achievement.completed:
                if achievement.update(value):
                    print(f"{Color.YELLOW}ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО: {achievement.name}{Color.END}")
                    print(f"{achievement.description}")
                    print(f"Награда: {achievement.reward_xp} опыта, {achievement.reward_gold} золота")
                    
                    self.xp += achievement.reward_xp
                    self.gold += achievement.reward_gold
                    
                    if self.xp >= self.xp_to_next_level:
                        self.level_up()

class Game:
    """Основной класс игры с улучшениями"""
    def __init__(self):
        self.player = None
        self.is_running = True
        self.game_world = {}
        self.quests_db = {}
        self.items_db = {}
        self.current_battle = None
        self.game_start_time = None
        self.difficulty = Difficulty.NORMAL
        self.version = "2.0.3"  # Обновили версию
        
        self.bordello_girls = []
        self.initialize_bordello()
        
        self.initialize_world()
        self.initialize_items()
        self.initialize_quests()
    
    def initialize_bordello(self):
        """Инициализация борделя"""
        girls = [
            BordelloGirl("Лилиана", "Массаж", 50, "Искусная массажистка, снимает усталость и напряжение"),
            BordelloGirl("Кларисса", "Танды", 30, "Страстная танцовщица, поднимает боевой дух"),
            BordelloGirl("Изольда", "Беседа", 20, "Умная собеседница, может дать полезные советы"),
            BordelloGirl("Маргарита", "Особое внимание", 100, "Опытная куртизанка, оказывает полный спектр услуг"),
            BordelloGirl("Бьянка", "Массаж", 40, "Молодая, но талантливая массажистка"),
            BordelloGirl("Эльвира", "Танды", 25, "Гибкая и грациозная танцовщица")
        ]
        
        self.bordello_girls = girls
    
    def initialize_world(self):
        """Инициализация игрового мира с улучшениями"""
        locations = [
            Location("Стартовая деревня", LocationType.TOWN, (1, 3),
                    "Тихая деревня, где начинаются многие приключения.",
                    ["Темный лес", "Гоблинские пещеры", "Таинственное болото"],
                    has_shop=True, has_tavern=True, has_bordello=True),
            
            Location("Темный лес", LocationType.FOREST, (1, 5),
                    "Густой лес, полный опасных существ.",
                    ["Стартовая деревня", "Забытые руины", "Лесная глушь"],
                    special_event_chance=0.2),
            
            Location("Гоблинские пещеры", LocationType.CAVE, (2, 6),
                    "Лабиринт пещер, кишащий гоблинами.",
                    ["Стартовая деревня", "Орочьи горы", "Подземные туннели"],
                    special_event_chance=0.15),
            
            Location("Забытые руины", LocationType.RUINS, (4, 8),
                    "Древние руины, хранящие множество тайн.",
                    ["Темный лес", "Драконье логово", "Древний храм"],
                    special_event_chance=0.25),
            
            Location("Орочьи горы", LocationType.MOUNTAIN, (6, 10),
                    "Высокие горы, где обосновались орки.",
                    ["Гоблинские пещеры", "Долина троллей", "Горная вершина"]),
            
            Location("Долина троллей", LocationType.DUNGEON, (8, 12),
                    "Глубокое ущелье, дом могущественных троллей.",
                    ["Орочьи горы", "Логово дракона", "Подземная река"]),
            
            Location("Логово дракона", LocationType.DUNGEON, (15, 20),
                    "Пылающая пещера, где обитает древний дракон.",
                    ["Долина троллей", "Вулканические земли"]),
            
            Location("Таинственное болото", LocationType.SWAMP, (3, 7),
                    "Топи, полные странных существ и ядовитых растений.",
                    ["Стартовая деревня", "Заброшенная хижина"]),
            
            Location("Лесная глушь", LocationType.FOREST, (5, 9),
                    "Самые глубины леса, куда редко ступает нога человека.",
                    ["Темный лес"]),
            
            Location("Заброшенная хижина", LocationType.RUINS, (7, 11),
                    "Старая хижина, от которой веет зловещей магией.",
                    ["Таинственное болото"]),
            
            Location("Роскошный бордель", LocationType.BORDELLO, (1, 100),
                    "Заведение с красивыми девушками и приятной атмосферой.",
                    ["Стартовая деревня"], has_bordello=True)
        ]
        
        for loc in locations:
            self.game_world[loc.name] = loc
        
        self.game_world["Стартовая деревня"].discovered = True
    
    def initialize_items(self):
        """Инициализация предметов - ДОБАВЛЕНЫ СПЕЦИАЛЬНЫЕ ЭФФЕКТЫ ДЛЯ ОРУЖИЯ"""
        # Оружие для всех классов с специальными эффектами
        weapons = [
            # Оружие для Воина
            Item("Деревянный меч", ItemType.WEAPON, value=10, damage=3, 
                description="Простой деревянный меч", durability=50, required_level=1,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Стальной меч", ItemType.WEAPON, value=50, damage=8, 
                description="Надежный стальной меч", durability=100, required_level=3,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Драконий клинок", ItemType.WEAPON, value=500, damage=25, 
                description="Меч, выкованный из когтя дракона", durability=150, required_level=15,
                character_classes=[CharacterClass.WARRIOR],
                special_effect="fire_damage"),  # Огненный урон
            
            Item("Секира варвара", ItemType.WEAPON, value=80, damage=12,
                description="Тяжелая, но смертоносная секира", durability=90, required_level=6,
                character_classes=[CharacterClass.WARRIOR],
                special_effect="armor_penetration"),  # Пробитие брони
            
            # Новое оружие для Воина
            Item("Молот Света", ItemType.WEAPON, value=200, damage=15,
                description="Благословенный молот, светящийся священным светом", 
                durability=120, required_level=8,
                character_classes=[CharacterClass.WARRIOR],
                special_effect="stun_chance"),  # Шанс оглушения
            
            Item("Ледяной меч", ItemType.WEAPON, value=180, damage=13,
                description="Меч, выкованный из вечного льда", 
                durability=110, required_level=7,
                character_classes=[CharacterClass.WARRIOR],
                special_effect="fire_damage"),  # Ледяной урон (используем fire_damage как базовый)
            
            # Оружие для Мага
            Item("Магический посох", ItemType.WEAPON, value=100, damage=5, mana=20, 
                description="Посох, усиливающий магию", durability=80, required_level=5,
                character_classes=[CharacterClass.MAGE]),
            
            Item("Жезл волшебника", ItemType.WEAPON, value=120, damage=6, mana=30,
                description="Мощный жезл для заклинаний", durability=70, required_level=7,
                character_classes=[CharacterClass.MAGE],
                special_effect="mana_steal"),  # Кража маны
            
            Item("Кристальный скипетр", ItemType.WEAPON, value=180, damage=8, mana=40,
                description="Скипетр с магическим кристаллом", durability=90, required_level=10,
                character_classes=[CharacterClass.MAGE],
                special_effect="fire_damage"),  # Магический урон
            
            Item("Книга заклинаний", ItemType.WEAPON, value=60, damage=3, mana=50,
                description="Древняя книга с магическими формулами", durability=40, required_level=3,
                character_classes=[CharacterClass.MAGE]),
            
            # Новое оружие для Мага
            Item("Посох Некроманта", ItemType.WEAPON, value=220, damage=10, mana=60,
                description="Посох, вырезанный из кости дракона", 
                durability=100, required_level=12,
                character_classes=[CharacterClass.MAGE],
                special_effect="life_steal"),  # Кража жизни
            
            Item("Жезл Стихий", ItemType.WEAPON, value=160, damage=9, mana=45,
                description="Жезл, контролирующий четыре стихии", 
                durability=85, required_level=9,
                character_classes=[CharacterClass.MAGE],
                special_effect="critical_chance"),  # Увеличенный шанс крита
            
            # Оружие для Лучника
            Item("Лук охотника", ItemType.WEAPON, value=40, damage=6, 
                description="Точный лук лесного охотника", durability=70, required_level=2,
                character_classes=[CharacterClass.ARCHER]),
            
            Item("Эльфийский лук", ItemType.WEAPON, value=150, damage=10,
                description="Искусно изготовленный эльфийский лук", durability=120, required_level=8,
                character_classes=[CharacterClass.ARCHER],
                special_effect="critical_chance"),  # Увеличенный шанс крита
            
            Item("Арбалет снайпера", ItemType.WEAPON, value=200, damage=12,
                description="Точный арбалет для дальних дистанций", durability=100, required_level=12,
                character_classes=[CharacterClass.ARCHER],
                special_effect="armor_penetration"),  # Пробитие брони
            
            Item("Короткий лук", ItemType.WEAPON, value=30, damage=4,
                description="Компактный лук для быстрой стрельбы", durability=50, required_level=1,
                character_classes=[CharacterClass.ARCHER]),
            
            # Новое оружие для Лучника
            Item("Лук Призрака", ItemType.WEAPON, value=170, damage=11,
                description="Лук, сделанный из призрачной древесины", 
                durability=95, required_level=10,
                character_classes=[CharacterClass.ARCHER],
                special_effect="poison"),  # Ядовитые стрелы
            
            Item("Арбалет Разрушителя", ItemType.WEAPON, value=250, damage=14,
                description="Мощный арбалет, пробивающий доспехи", 
                durability=110, required_level=14,
                character_classes=[CharacterClass.ARCHER],
                special_effect="armor_penetration"),  # Сильное пробитие брони
            
            # Оружие для Разбойника
            Item("Кинжалы разбойника", ItemType.WEAPON, value=60, damage=7, 
                description="Пара острых кинжалов", durability=60, required_level=4,
                character_classes=[CharacterClass.ROGUE]),
            
            Item("Теневые клинки", ItemType.WEAPON, value=140, damage=9,
                description="Клинки, невидимые в темноте", durability=80, required_level=9,
                character_classes=[CharacterClass.ROGUE],
                special_effect="poison"),  # Ядовитые клинки
            
            Item("Отравленные кинжалы", ItemType.WEAPON, value=90, damage=6,
                description="Кинжалы с ядом", durability=60, required_level=5,
                character_classes=[CharacterClass.ROGUE],
                special_effect="poison"),  # Яд
            
            Item("Стилет", ItemType.WEAPON, value=45, damage=5,
                description="Тонкий кинжал для точных ударов", durability=40, required_level=2,
                character_classes=[CharacterClass.ROGUE]),
            
            # Новое оружие для Разбойника
            Item("Кинжалы Убийцы", ItemType.WEAPON, value=190, damage=11,
                description="Клинки, созданные для бесшумных убийств", 
                durability=75, required_level=11,
                character_classes=[CharacterClass.ROGUE],
                special_effect="critical_chance"),  # Высокий шанс крита
            
            Item("Когти Призрака", ItemType.WEAPON, value=130, damage=8,
                description="Парные клинки, оставляющие призрачные следы", 
                durability=65, required_level=6,
                character_classes=[CharacterClass.ROGUE],
                special_effect="life_steal"),  # Кража жизни
        ]
        
        # Броня с указанием конкретных слотов и классов
        armors = [
            # Броня для воина
            Item("Кожаная броня", ItemType.ARMOR, value=20, defense=3, 
                description="Прочная кожаная броня", durability=60, required_level=1, 
                armor_slot="armor", character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Кольчуга", ItemType.ARMOR, value=80, defense=7, 
                description="Тяжелая, но надежная кольчуга", durability=100, required_level=4, 
                armor_slot="armor", character_classes=[CharacterClass.WARRIOR]),
            
            Item("Доспех дракона", ItemType.ARMOR, value=400, defense=20, health=50, 
                description="Доспехи из драконьей чешуи", durability=200, required_level=15, 
                armor_slot="armor", character_classes=[CharacterClass.WARRIOR]),
            
            Item("Пластинчатый доспех", ItemType.ARMOR, value=120, defense=10,
                description="Тяжелый пластинчатый доспех", durability=110, required_level=7, 
                armor_slot="armor", character_classes=[CharacterClass.WARRIOR]),
            
            Item("Чешуйчатая броня", ItemType.ARMOR, value=60, defense=5,
                description="Броня из металлических чешуек", durability=80, required_level=3,
                armor_slot="armor", character_classes=[CharacterClass.WARRIOR]),
            
            # Броня для мага
            Item("Мантия мага", ItemType.ARMOR, value=60, defense=2, mana=30, 
                description="Мантия, усиливающая магическую силу", durability=50, required_level=3, 
                armor_slot="armor", character_classes=[CharacterClass.MAGE]),
            
            Item("Роба волшебника", ItemType.ARMOR, value=100, defense=3, mana=50,
                description="Роба, сотканная из магических нитей", durability=60, required_level=6,
                armor_slot="armor", character_classes=[CharacterClass.MAGE]),
            
            Item("Плащ архимага", ItemType.ARMOR, value=250, defense=5, mana=80,
                description="Плащ древнего архимага", durability=90, required_level=12,
                armor_slot="armor", character_classes=[CharacterClass.MAGE]),
            
            # Броня для лучника
            Item("Кожаный доспех лучника", ItemType.ARMOR, value=40, defense=4,
                description="Легкий доспех для лучников", durability=70, required_level=2,
                armor_slot="armor", character_classes=[CharacterClass.ARCHER]),
            
            Item("Камуфляжный плащ", ItemType.ARMOR, value=70, defense=3,
                description="Плащ для маскировки в лесу", durability=60, required_level=4,
                armor_slot="armor", character_classes=[CharacterClass.ARCHER]),
            
            # Броня для разбойника
            Item("Кожаная куртка", ItemType.ARMOR, value=35, defense=3,
                description="Прочная кожаная куртка", durability=50, required_level=2,
                armor_slot="armor", character_classes=[CharacterClass.ROGUE]),
            
            Item("Теневой плащ", ItemType.ARMOR, value=90, defense=4,
                description="Плащ, скрывающий в тенях", durability=65, required_level=5,
                armor_slot="armor", character_classes=[CharacterClass.ROGUE]),
        ]
        
        # Шлемы
        helmets = [
            Item("Кожаный шлем", ItemType.HELMET, value=15, defense=2,
                description="Прочный кожаный шлем", durability=40, required_level=1,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Железный шлем", ItemType.HELMET, value=40, defense=4,
                description="Надежный железный шлем", durability=70, required_level=3,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Магический капюшон", ItemType.HELMET, value=60, defense=1, mana=20,
                description="Капюшон, усиливающий магию", durability=50, required_level=4,
                character_classes=[CharacterClass.MAGE]),
            
            Item("Драконий шлем", ItemType.HELMET, value=150, defense=8, health=20,
                description="Шлем из драконьей чешуи", durability=120, required_level=12,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Капюшон лучника", ItemType.HELMET, value=30, defense=2,
                description="Капюшон для защиты от ветра", durability=35, required_level=2,
                character_classes=[CharacterClass.ARCHER]),
            
            Item("Маска разбойника", ItemType.HELMET, value=25, defense=1,
                description="Маска, скрывающая лицо", durability=30, required_level=1,
                character_classes=[CharacterClass.ROGUE]),
        ]
        
        # Перчатки
        gloves = [
            Item("Кожаные перчатки", ItemType.GLOVES, value=10, defense=1,
                description="Прочные кожаные перчатки", durability=30, required_level=1,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Железные перчатки", ItemType.GLOVES, value=30, defense=2,
                description="Железные перчатки с усилением", durability=50, required_level=3,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Перчатки ловкости", ItemType.GLOVES, value=50, defense=1, 
                description="Перчатки, увеличивающие ловкость", durability=40, required_level=5,
                character_classes=[CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Магические перчатки", ItemType.GLOVES, value=40, defense=1, mana=15,
                description="Перчатки, усиливающие магию", durability=35, required_level=4,
                character_classes=[CharacterClass.MAGE]),
            
            Item("Перчатки стрелка", ItemType.GLOVES, value=35, defense=1,
                description="Перчатки для точной стрельбы", durability=30, required_level=3,
                character_classes=[CharacterClass.ARCHER]),
        ]
        
        # Сапоги
        boots = [
            Item("Кожаные сапоги", ItemType.BOOTS, value=10, defense=1,
                description="Прочные кожаные сапоги", durability=30, required_level=1,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE, CharacterClass.MAGE]),
            
            Item("Железные сапоги", ItemType.BOOTS, value=30, defense=2,
                description="Железные сапоги с защитой", durability=50, required_level=3,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Сапоги скорости", ItemType.BOOTS, value=40, defense=1,
                description="Сапоги, увеличивающие скорость", durability=40, required_level=4,
                character_classes=[CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Магические сапоги", ItemType.BOOTS, value=45, defense=1, mana=10,
                description="Сапоги, усиливающие магию", durability=35, required_level=4,
                character_classes=[CharacterClass.MAGE]),
            
            Item("Сапоги тишины", ItemType.BOOTS, value=55, defense=1,
                description="Сапоги, позволяющие двигаться бесшумно", durability=40, required_level=6,
                character_classes=[CharacterClass.ROGUE]),
        ]
        
        # Кольца
        rings = [
            Item("Кольцо защиты", ItemType.RING, value=80, defense=3,
                description="Кольцо, увеличивающее защиту", required_level=3,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Кольцо маны", ItemType.RING, value=70, mana=20,
                description="Кольцо, увеличивающее ману", required_level=3,
                character_classes=[CharacterClass.MAGE]),
            
            Item("Кольцо силы", ItemType.RING, value=90, damage=2,
                description="Кольцо, увеличивающее силу", required_level=4,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Кольцо ловкости", ItemType.RING, value=85,
                description="Кольцо, увеличивающее ловкость", required_level=4,
                character_classes=[CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Кольцо здоровья", ItemType.RING, value=60, health=20,
                description="Кольцо, увеличивающее здоровье", required_level=2,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE, CharacterClass.MAGE]),
        ]
        
        # Амулеты
        amulets = [
            Item("Амулет защиты", ItemType.AMULET, value=100, defense=5,
                description="Амулет, увеличивающий защиту", required_level=5,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Амулет магии", ItemType.AMULET, value=120, mana=30,
                description="Амулет, усиливающий магию", required_level=6,
                character_classes=[CharacterClass.MAGE]),
            
            Item("Амулет силы", ItemType.AMULET, value=110, damage=3,
                description="Амулет, увеличивающий силу", required_level=6,
                character_classes=[CharacterClass.WARRIOR]),
            
            Item("Амулет удачи", ItemType.AMULET, value=95,
                description="Амулет, увеличивающий удачу", required_level=4,
                character_classes=[CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Амулет жизни", ItemType.AMULET, value=130, health=30,
                description="Амулет, увеличивающее здоровье", required_level=7,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER, CharacterClass.ROGUE, CharacterClass.MAGE]),
        ]
        
        # Зелья
        potions = [
            Item("Зелье здоровья", ItemType.POTION, value=20, health=50, 
                description="Восстанавливает здоровье", required_level=1),
            
            Item("Зелье маны", ItemType.POTION, value=25, mana=30, 
                description="Восстанавливает ману", required_level=1),
            
            Item("Сильное зелье здоровья", ItemType.POTION, value=50, health=100, 
                description="Сильно восстанавливает здоровье", required_level=3),
            
            Item("Эликсир опыта", ItemType.POTION, value=100, 
                description="Дает 100 опыта", required_level=5),
            
            Item("Зелье силы", ItemType.POTION, value=40, 
                description="Увеличивает силу на 5 на 10 минут", required_level=4,
                character_classes=[CharacterClass.WARRIOR, CharacterClass.ARCHER]),
            
            Item("Антидот", ItemType.POTION, value=30, 
                description="Лечит от яда", required_level=2),
            
            Item("Эликсир удачи", ItemType.POTION, value=60,
                description="Увеличивает удачу на 3 на 1 час", required_level=6),
            
            Item("Зелье ловкости", ItemType.POTION, value=45,
                description="Увеличивает ловкость на 5 на 10 минут", required_level=4,
                character_classes=[CharacterClass.ARCHER, CharacterClass.ROGUE]),
            
            Item("Зелье интеллекта", ItemType.POTION, value=55,
                description="Увеличивает интеллект на 5 на 10 минут", required_level=4,
                character_classes=[CharacterClass.MAGE]),
        ]
        
        # Свитки
        scrolls = [
            Item("Свиток телепортации", ItemType.SCROLL, value=100,
                description="Телепортирует в Стартовую деревню", required_level=1),
            
            Item("Свиток идентификации", ItemType.SCROLL, value=80,
                description="Позволяет идентифицировать предметы", required_level=3),
            
            Item("Свиток воскрешения", ItemType.SCROLL, value=500,
                description="Воскрешает павшего союзника", required_level=10),
            
            Item("Свиток щита", ItemType.SCROLL, value=120,
                description="Создает магический щит", required_level=4,
                character_classes=[CharacterClass.MAGE]),
            
            Item("Свиток огня", ItemType.SCROLL, value=150,
                description="Вызывает огненный шар", required_level=5,
                character_classes=[CharacterClass.MAGE]),
        ]
        
        # Собираем все предметы в базу данных
        all_items = weapons + armors + helmets + gloves + boots + rings + amulets + potions + scrolls
        for item in all_items:
            self.items_db[item.name] = item
    
    def initialize_quests(self):
        """Инициализация квестов"""
        main_quest = Quest(
            "Угроза дракона",
            "Древний дракон пробудился и угрожает королевству. Победите его!",
            "Логово дракона",
            1000, 500, 15, "main"
        )
        main_quest.add_objective("Победить дракона", "Дракон", 1)
        main_quest.add_reward_item(self.items_db["Драконий клинок"].copy())
        main_quest.add_reward_item(self.items_db["Доспех дракона"].copy())
        self.quests_db[main_quest.id] = main_quest
        
        quest1 = Quest(
            "Очистить лес",
            "Темный лес кишит волками. Убейте 5 волков.",
            "Темный лес",
            150, 50, 2, "side"
        )
        quest1.add_objective("Убить волков", "Волк", 5)
        quest1.add_reward_item(self.items_db["Зелье здоровья"].copy())
        self.quests_db[quest1.id] = quest1
        
        quest2 = Quest(
            "Гоблинская проблема",
            "Гоблины нападают на деревню. Убейте 10 гоблинов.",
            "Гоблинские пещеры",
            300, 100, 3, "side"
        )
        quest2.add_objective("Убить гоблинов", "Гоблин", 10)
        quest2.add_reward_item(self.items_db["Стальной меч"].copy())
        self.quests_db[quest2.id] = quest2
        
        quest3 = Quest(
            "Сокровища руин",
            "Найдите древний артефакт в Забытых руинах.",
            "Забытые руины",
            500, 200, 5, "side"
        )
        quest3.add_objective("Найти артефакт", "Артефакт", 1)
        quest3.add_reward_item(self.items_db["Магический посох"].copy())
        self.quests_db[quest3.id] = quest3
        
        quest4 = Quest(
            "Болотные твари",
            "Очистите болото от пауков.",
            "Таинственное болото",
            250, 80, 4, "side"
        )
        quest4.add_objective("Убить пауков", "Паук", 8)
        quest4.add_reward_item(self.items_db["Антидот"].copy())
        self.quests_db[quest4.id] = quest4
        
        quest5 = Quest(
            "Особое поручение",
            "Навестите бордель и получите особую услугу.",
            "Роскошный бордель",
            100, 50, 3, "side"
        )
        quest5.add_objective("Посетить бордель", "Бордель", 1)
        quest5.add_reward_item(self.items_db["Зелье здоровья"].copy())
        self.quests_db[quest5.id] = quest5
    
    # ОПТИМИЗАЦИЯ: создадим общие методы для вывода
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Вывод заголовка"""
        print(f"{Color.CYAN}{'='*70}{Color.END}")
        print(f"{Color.BOLD}{Color.YELLOW}{title:^70}{Color.END}")
        print(f"{Color.CYAN}{'='*70}{Color.END}")
    
    def print_menu(self, options: List[Tuple[str, str]]):
        """Вывод меню"""
        for i, (key, description) in enumerate(options, 1):
            print(f"{Color.GREEN}{i}.{Color.END} {description}")
        print(f"{Color.CYAN}{'-'*70}{Color.END}")
    
    def get_choice(self, min_choice: int, max_choice: int) -> int:
        """Получение выбора от пользователя"""
        while True:
            try:
                choice = input(f"{Color.WHITE}Ваш выбор ({min_choice}-{max_choice}): {Color.END}")
                
                if choice.lower() in ['выход', 'exit', 'quit']:
                    confirm = input("Вы уверены, что хотите выйти? (y/n): ")
                    if confirm.lower() == 'y':
                        print(f"{Color.YELLOW}До свидания!{Color.END}")
                        sys.exit(0)
                    else:
                        continue
                
                choice = int(choice)
                if min_choice <= choice <= max_choice:
                    return choice
                print(f"{Color.RED}Пожалуйста, введите число от {min_choice} до {max_choice}{Color.END}")
            except ValueError:
                print(f"{Color.RED}Пожалуйста, введите число{Color.END}")
    
    def create_character(self):
        """Создание персонажа"""
        self.clear_screen()
        self.print_header("СОЗДАНИЕ ПЕРСОНАЖА")
        
        print(f"{Color.YELLOW}Выберите сложность игры:{Color.END}")
        print("1. Легкий - для новичков (бониус к здоровью и урону)")
        print("2. Нормальный - стандартный опыт")
        print("3. Сложный - для опытных игроков (штраф к здоровью и урону)")
        print("4. Безумный - настоящий вызов (большие штрафы)")
        
        diff_choice = self.get_choice(1, 4)
        difficulty_map = {
            1: Difficulty.EASY,
            2: Difficulty.NORMAL,
            3: Difficulty.HARD,
            4: Difficulty.INSANE
        }
        self.difficulty = difficulty_map[diff_choice]
        
        print(f"\n{Color.WHITE}Введите имя вашего персонажа (3-15 символов):{Color.END}")
        name = input("> ").strip()
        while not (3 <= len(name) <= 15):
            print(f"{Color.RED}Имя должно содержать от 3 до 15 символов!{Color.END}")
            name = input("> ").strip()
        
        self.player = Player(name, self.difficulty)
        
        self.clear_screen()
        self.print_header("ВЫБОР КЛАССА")
        
        print(f"Имя: {Color.YELLOW}{self.player.name}{Color.END}")
        print(f"Сложность: {Color.CYAN}{self.difficulty.value}{Color.END}")
        print()
        
        classes = [
            ("1", f"{Color.RED}Воин{Color.END} - Сильный и выносливый боец (Высокая сила и здоровье)"),
            ("2", f"{Color.BLUE}Маг{Color.END} - Могущественный заклинатель (Высокий интеллект и мана)"),
            ("3", f"{Color.GREEN}Лучник{Color.END} - Меткий стрелок (Высокая ловкость и точность)"),
            ("4", f"{Color.PURPLE}Разбойник{Color.END} - Ловкий и хитрый (Высокая ловкость и удача)")
        ]
        
        for key, desc in classes:
            print(f"{key}. {desc}")
        
        print(f"\n{Color.YELLOW}Выберите класс:{Color.END}")
        class_choice = self.get_choice(1, 4)
        
        class_map = {
            1: CharacterClass.WARRIOR,
            2: CharacterClass.MAGE,
            3: CharacterClass.ARCHER,
            4: CharacterClass.ROGUE
        }
        
        self.player.set_class(class_map[class_choice])
        
        starter_items = {
            CharacterClass.WARRIOR: ["Деревянный меч", "Кожаная броня", "Кожаный шлем", "Кожаные перчатки", "Кожаные сапоги"],
            CharacterClass.MAGE: ["Магический посох", "Мантия мага", "Магический капюшон", "Кожаные перчатки", "Кожаные сапоги"],
            CharacterClass.ARCHER: ["Лук охотника", "Кожаная броня", "Кожаный шлем", "Кожаные перчатки", "Кожаные сапоги"],
            CharacterClass.ROGUE: ["Кинжалы разбойника", "Кожаная броня", "Кожаный шлем", "Кожаные перчатки", "Кожаные сапоги"]
        }
        
        starter_potions = ["Зелье здоровья", "Зелье здоровья", "Зелье маны"]
        
        for item_name in starter_items.get(self.player.character_class, []):
            if item_name in self.items_db:
                self.player.add_item(self.items_db[item_name].copy())
        
        for potion_name in starter_potions:
            if potion_name in self.items_db:
                self.player.add_item(self.items_db[potion_name].copy())
        
        for item in self.player.inventory[:]:
            if item.item_type == ItemType.WEAPON:
                self.player.equip_item(item)
            elif item.item_type in [ItemType.ARMOR, ItemType.HELMET, ItemType.GLOVES, ItemType.BOOTS]:
                self.player.equip_item(item)
        
        self.clear_screen()
        self.print_header("ПЕРСОНАЖ СОЗДАН")
        print(f"Добро пожаловать, {Color.YELLOW}{self.player.name}{Color.END}!")
        print(f"Класс: {Color.CYAN}{self.player.character_class.value}{Color.END}")
        print(f"Сложность: {Color.PURPLE}{self.difficulty.value}{Color.END}")
        print(f"Уровень: {Color.GREEN}{self.player.level}{Color.END}")
        print(f"Здоровье: {Color.GREEN}{self.player.health}/{self.player.max_health}{Color.END}")
        print(f"Мана: {Color.BLUE}{self.player.mana}/{self.player.max_mana}{Color.END}")
        print(f"Золото: {Color.YELLOW}{self.player.gold}{Color.END}")
        
        print(f"\n{Color.BOLD}ХАРАКТЕРИСТИКИ:{Color.END}")
        stat_names = {
            "strength": "Сила",
            "dexterity": "Ловкость",
            "intelligence": "Интеллект",
            "constitution": "Телосложение",
            "luck": "Удача"
        }
        for stat, value in self.player.stats.items():
            print(f"  {stat_names.get(stat, stat)}: {value}")
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы начать приключение...{Color.END}")
    
    # ОПТИМИЗАЦИЯ: унифицированный метод для создания полосок
    def create_bar(self, current: int, maximum: int, length: int = 20, color_good: str = Color.GREEN, 
                  color_medium: str = Color.GREEN, color_bad: str = Color.END) -> str:
        """Создание полоски с улучшениями"""
        if maximum <= 0:
            return f"[{'█' * length}] 0/0"
        
        filled = int((current / maximum) * length)
        if filled < 0:
            filled = 0
        if filled > length:
            filled = length
            
        empty = length - filled
        
        percent = (current / maximum) * 100
        if percent > 70:
            color = color_good
        elif percent > 30:
            color = color_medium
        else:
            color = color_bad
            
        return f"[{color}{'█' * filled}{color_bad}{'█' * empty}{Color.END}] {current}/{maximum}"
    
    def show_status(self):
        """Показать статус персонажа"""
        self.clear_screen()
        self.print_header("СТАТУС ПЕРСОНАЖА")
        
        print(f"Имя: {Color.YELLOW}{self.player.name}{Color.END}")
        print(f"Класс: {Color.CYAN}{self.player.character_class.value}{Color.END}")
        print(f"Сложность: {Color.PURPLE}{self.player.difficulty.value}{Color.END}")
        print(f"Уровень: {Color.GREEN}{self.player.level}{Color.END}")
        print(f"Опыт: {self.player.xp}/{self.player.xp_to_next_level}")
        
        health_bar = self.create_bar(self.player.health, self.player.max_health, 25)
        mana_bar = self.create_bar(self.player.mana, self.player.max_mana, 25, Color.BLUE, Color.BLUE, Color.PURPLE)
        
        print(f"Здоровье: {health_bar}")
        print(f"Мана:     {mana_bar}")
        print(f"Золото: {Color.YELLOW}{self.player.gold}{Color.END}")
        
        print(f"\n{Color.BOLD}ХАРАКТЕРИСТИКИ:{Color.END}")
        stat_names = {
            "strength": "Сила",
            "dexterity": "Ловкость",
            "intelligence": "Интеллект",
            "constitution": "Телосложение",
            "luck": "Удача"
        }
        for stat, value in self.player.stats.items():
            bonus = self.player.get_stat_bonus(stat)
            print(f"  {stat_names.get(stat, stat)}: {value} (бонус: +{bonus})")
        
        print(f"\n{Color.BOLD}ЭКИПИРОВКА:{Color.END}")
        slot_names = {
            "weapon": "Оружие",
            "armor": "Броня",
            "helmet": "Шлем",
            "gloves": "Перчатки",
            "boots": "Сапоги",
            "ring": "Кольцо",
            "amulet": "Амулет"
        }
        
        for slot, item in self.player.equipped.items():
            slot_name = slot_names.get(slot, slot)
            if item:
                print(f"  {slot_name}: {item.get_colored_name()}")
                if item.durability < item.max_durability * 0.3:
                    print(f"    {Color.RED}Внимание: низкая прочность!{Color.END}")
                # Показываем специальный эффект оружия
                if slot == "weapon" and item.special_effect:
                    effect_names = {
                        "fire_damage": "Огненный урон",
                        "mana_steal": "Кража маны",
                        "critical_chance": "Шанс крита",
                        "poison": "Яд",
                        "life_steal": "Кража здоровья",
                        "stun_chance": "Оглушение",
                        "armor_penetration": "Пробитие брони"
                    }
                    effect_name = effect_names.get(item.special_effect, item.special_effect)
                    print(f"    {Color.CYAN}Эффект: {effect_name}{Color.END}")
            else:
                print(f"  {slot_name}: {Color.WHITE}Нет{Color.END}")
        
        if self.player.killed_enemies:
            print(f"\n{Color.BOLD}УБИТО ВРАГОВ:{Color.END}")
            total_killed = sum(self.player.killed_enemies.values())
            print(f"  Всего: {total_killed}")
            
            for enemy_type, count in sorted(self.player.killed_enemies.items(), 
                                          key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {enemy_type}: {count}")
        
        if self.game_start_time:
            play_time = datetime.now() - self.game_start_time
            hours = play_time.seconds // 3600
            minutes = (play_time.seconds % 3600) // 60
            seconds = play_time.seconds % 60
            print(f"\nВремя игры: {hours}ч {minutes}м {seconds}с")
        
        completed_achievements = [a for a in self.player.achievements if a.completed]
        if completed_achievements:
            print(f"\n{Color.BOLD}ДОСТИЖЕНИЯ ({len(completed_achievements)}/{len(self.player.achievements)}):{Color.END}")
            for i, achievement in enumerate(completed_achievements[:3], 1):
                print(f"  {i}. {achievement.name} - {achievement.description}")
            
            if len(completed_achievements) > 3:
                print(f"  ... и еще {len(completed_achievements) - 3}")
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы вернуться...{Color.END}")
    
    def show_inventory(self):
        """Показать инвентарь"""
        while True:
            self.clear_screen()
            self.print_header("ИНВЕНТАРЬ")
            
            print(f"Золото: {Color.YELLOW}{self.player.gold}{Color.END}")
            print(f"Свободно мест: {len(self.player.inventory)}/40")
            
            if not self.player.inventory:
                print(f"\n{Color.YELLOW}Инвентарь пуст{Color.END}")
            else:
                items_by_type = {}
                for item in self.player.inventory:
                    if item.item_type not in items_by_type:
                        items_by_type[item.item_type] = []
                    items_by_type[item.item_type].append(item)
                
                item_index = 1
                item_map = {}
                
                for item_type, items in sorted(items_by_type.items(), key=lambda x: x[0].value):
                    print(f"\n{Color.BOLD}{item_type.value}:{Color.END}")
                    for item in items:
                        level_req = f" [Требует уровень {item.required_level}]" if item.required_level > 1 else ""
                        print(f"  {item_index}. {item.get_colored_name()}{level_req}")
                        print(f"     {item.description}")
                        
                        stats = []
                        if item.damage > 0:
                            stats.append(f"Урон: {item.damage}")
                        if item.defense > 0:
                            stats.append(f"Защита: {item.defense}")
                        if item.health > 0:
                            stats.append(f"Здоровье: +{item.health}")
                        if item.mana > 0:
                            stats.append(f"Мана: +{item.mana}")
                        
                        if stats:
                            print(f"     {', '.join(stats)}")
                        
                        # Показываем специальный эффект для оружия
                        if item.special_effect:
                            effect_names = {
                                "fire_damage": "Огненный урон",
                                "mana_steal": "Кража маны",
                                "critical_chance": "Шанс крита",
                                "poison": "Яд",
                                "life_steal": "Кража здоровья",
                                "stun_chance": "Оглушение",
                                "armor_penetration": "Пробитие брони"
                            }
                            effect_name = effect_names.get(item.special_effect, item.special_effect)
                            print(f"     {Color.CYAN}Эффект: {effect_name}{Color.END}")
                        
                        print(f"     Цена: {item.value} золота")
                        item_map[item_index] = item
                        item_index += 1
            
            print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
            options = [
                ("1", "Использовать предмет"),
                ("2", "Экипировать предмет"),
                ("3", "Снять экипировку"),
                ("4", "Выбросить предмет"),
                ("5", "Отсортировать инвентарь"),
                ("6", "Вернуться")
            ]
            
            for key, desc in options:
                print(f"{key}. {desc}")
            
            choice = self.get_choice(1, 6)
            
            if choice == 1:
                if not self.player.inventory:
                    print(f"{Color.RED}Нет предметов для использования{Color.END}")
                    time.sleep(1)
                    continue
                
                print(f"\n{Color.WHITE}Выберите предмет для использования:{Color.END}")
                item_choice = self.get_choice(1, len(self.player.inventory))
                
                item = None
                current_index = 1
                for inv_item in self.player.inventory:
                    if current_index == item_choice:
                        item = inv_item
                        break
                    current_index += 1
                
                if item:
                    self.use_item(item)
            
            elif choice == 2:
                if not self.player.inventory:
                    print(f"{Color.RED}Нет предметов для экипировки{Color.END}")
                    time.sleep(1)
                    continue
                
                equippable_items = [item for item in self.player.inventory 
                                  if item.item_type in [ItemType.WEAPON, ItemType.ARMOR, 
                                                       ItemType.HELMET, ItemType.GLOVES, 
                                                       ItemType.BOOTS, ItemType.RING, 
                                                       ItemType.AMULET]]
                
                if not equippable_items:
                    print(f"{Color.RED}Нет предметов, которые можно экипировать{Color.END}")
                    time.sleep(1)
                    continue
                
                print(f"\n{Color.WHITE}Выберите предмет для экипировки:{Color.END}")
                for i, item in enumerate(equippable_items, 1):
                    print(f"{i}. {item.get_colored_name()} ({item.item_type.value})")
                
                item_choice = self.get_choice(1, len(equippable_items))
                item = equippable_items[item_choice - 1]
                
                if item:
                    if self.player.equip_item(item):
                        print(f"{Color.GREEN}Предмет экипирован!{Color.END}")
                        # Показываем эффект оружия
                        if item.item_type == ItemType.WEAPON and item.special_effect:
                            effect_names = {
                                "fire_damage": "Это оружие наносит дополнительный огненный урон!",
                                "mana_steal": "Это оружие крадет ману у врагов!",
                                "critical_chance": "Это оружие увеличивает шанс критического удара!",
                                "poison": "Это оружие отравляет врагов!",
                                "life_steal": "Это оружие крадет здоровье у врагов!",
                                "stun_chance": "Это оружие может оглушить врага!",
                                "armor_penetration": "Это оружие пробивает броню врагов!"
                            }
                            effect_desc = effect_names.get(item.special_effect, "")
                            if effect_desc:
                                print(f"{Color.CYAN}{effect_desc}{Color.END}")
                    else:
                        print(f"{Color.RED}Не удалось экипировать предмет{Color.END}")
                    time.sleep(2)
            
            elif choice == 3:
                equipped_items = [(slot, item) for slot, item in self.player.equipped.items() 
                                if item is not None]
                
                if not equipped_items:
                    print(f"{Color.YELLOW}Нет экипированных предметов{Color.END}")
                    time.sleep(1)
                    continue
                
                print(f"\n{Color.WHITE}Выберите предмет для снятия:{Color.END}")
                for i, (slot, item) in enumerate(equipped_items, 1):
                    slot_name = {
                        "weapon": "Оружие",
                        "armor": "Броня",
                        "helmet": "Шлем",
                        "gloves": "Перчатки",
                        "boots": "Сапоги",
                        "ring": "Кольцо",
                        "amulet": "Амулет"
                    }.get(slot, slot)
                    print(f"{i}. {slot_name}: {item.get_colored_name()}")
                
                item_choice = self.get_choice(1, len(equipped_items))
                slot, _ = equipped_items[item_choice - 1]
                
                if self.player.unequip_item(slot):
                    print(f"{Color.GREEN}Предмет снят!{Color.END}")
                time.sleep(1)
            
            elif choice == 4:
                if not self.player.inventory:
                    print(f"{Color.RED}Нет предметов для удаления{Color.END}")
                    time.sleep(1)
                    continue
                
                print(f"\n{Color.WHITE}Выберите предмет для удаления:{Color.END}")
                item_choice = self.get_choice(1, len(self.player.inventory))
                
                item = None
                current_index = 1
                for inv_item in self.player.inventory:
                    if current_index == item_choice:
                        item = inv_item
                        break
                    current_index += 1
                
                if item:
                    print(f"\n{Color.YELLOW}Вы уверены, что хотите выбросить {item.name}?{Color.END}")
                    print("1. Да, выбросить")
                    print("2. Нет, оставить")
                    
                    confirm = self.get_choice(1, 2)
                    if confirm == 1:
                        self.player.remove_item(item)
                        print(f"{Color.YELLOW}Предмет выброшен{Color.END}")
                        time.sleep(1)
            
            elif choice == 5:
                self.sort_inventory()
                print(f"{Color.GREEN}Инвентарь отсортирован!{Color.END}")
                time.sleep(1)
            
            elif choice == 6:
                break
    
    def sort_inventory(self):
        """Сортировка инвентаря"""
        self.player.inventory.sort(key=lambda x: (
            x.item_type.value,
            {"Обычный": 0, "Необычный": 1, "Редкий": 2, "Эпический": 3, "Легендарный": 4}.get(x.rarity, 0),
            x.name
        ))
    
    def use_item(self, item: Item):
        """Использовать предмет"""
        if item.item_type == ItemType.POTION:
            if item.health > 0:
                old_health = self.player.health
                self.player.heal(item.health)
                healed = self.player.health - old_health
                print(f"{Color.GREEN}Вы восстановили {healed} здоровья!{Color.END}")
            
            if item.mana > 0:
                old_mana = self.player.mana
                self.player.restore_mana(item.mana)
                restored = self.player.mana - old_mana
                print(f"{Color.BLUE}Вы восстановили {restored} маны!{Color.END}")
            
            if item.name == "Эликсир опыта":
                self.player.gain_xp(100)
                print(f"{Color.YELLOW}Вы получили 100 опыта!{Color.END}")
            
            if item.name == "Зелье силы":
                self.player.stats["strength"] += 5
                print(f"{Color.GREEN}Ваша сила увеличена на 5 на 10 минут!{Color.END}")
            
            elif item.name == "Эликсир удачи":
                self.player.stats["luck"] += 3
                print(f"{Color.GREEN}Ваша удача увеличена на 3 на 1 час!{Color.END}")
            
            elif item.name == "Зелье ловкости":
                self.player.stats["dexterity"] += 5
                print(f"{Color.GREEN}Ваша ловкость увеличена на 5 на 10 минут!{Color.END}")
            
            elif item.name == "Зелье интеллекта":
                self.player.stats["intelligence"] += 5
                print(f"{Color.GREEN}Ваш интеллект увеличена на 5 на 10 минут!{Color.END}")
            
            self.player.remove_item(item)
        
        elif item.item_type == ItemType.SCROLL:
            if item.name == "Свиток телепортации":
                self.player.location = "Стартовая деревня"
                print(f"{Color.YELLOW}Вы телепортируетесь в Стартовую деревню!{Color.END}")
            elif item.name == "Свиток идентификации":
                print(f"{Color.YELLOW}Вы использовали свиток идентификации.{Color.END}")
            elif item.name == "Свиток воскрешения":
                print(f"{Color.YELLOW}Свиток воскрешения можно использовать только в бою.{Color.END}")
            
            self.player.remove_item(item)
        
        else:
            print(f"{Color.RED}Этот предмет нельзя использовать напрямую{Color.END}")
        
        time.sleep(2)
    
    def show_quests(self):
        """Показать квесты"""
        self.clear_screen()
        self.print_header("КВЕСТЫ")
        
        if not self.player.quests:
            print(f"{Color.YELLOW}У вас нет активных квестов{Color.END}")
            print("Посетите таверну или поговорите с жителями, чтобы получить квесты.")
        else:
            main_quests = [q for q in self.player.quests if q.quest_type == "main"]
            side_quests = [q for q in self.player.quests if q.quest_type == "side"]
            daily_quests = [q for q in self.player.quests if q.quest_type == "daily"]
            
            if main_quests:
                print(f"\n{Color.BOLD}ОСНОВНЫЕ КВЕСТЫ:{Color.END}")
                for quest in main_quests:
                    self.print_quest_info(quest)
            
            if side_quests:
                print(f"\n{Color.BOLD}ПОБОЧНЫЕ КВЕСТЫ:{Color.END}")
                for quest in side_quests:
                    self.print_quest_info(quest)
            
            if daily_quests:
                print(f"\n{Color.BOLD}ЕЖЕДНЕВНЫЕ КВЕСТЫ:{Color.END}")
                for quest in daily_quests:
                    self.print_quest_info(quest)
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы вернуться...{Color.END}")
    
    def print_quest_info(self, quest: Quest):
        """Вывод информации о квесте"""
        status_color = {
            QuestStatus.NOT_STARTED: Color.WHITE,
            QuestStatus.IN_PROGRESS: Color.YELLOW,
            QuestStatus.COMPLETED: Color.GREEN,
            QuestStatus.FAILED: Color.RED
        }.get(quest.status, Color.WHITE)
        
        print(f"\n{Color.BOLD}{quest.name}{Color.END}")
        print(f"Статус: {status_color}{quest.status.value}{Color.END}")
        print(f"Описание: {quest.description}")
        
        if quest.location:
            print(f"Локация: {quest.location}")
        
        if quest.time_limit > 0 and quest.start_time:
            elapsed = (datetime.now() - quest.start_time).seconds / 60
            remaining = max(0, quest.time_limit - elapsed)
            print(f"Осталось времени: {int(remaining)} минут")
        
        print(f"Награда: {quest.reward_xp} опыта, {quest.reward_gold} золота")
        
        if quest.reward_items:
            print(f"Дополнительные награды:")
            for item in quest.reward_items:
                print(f"  - {item.get_colored_name()}")
        
        if quest.objectives:
            print(f"\n{Color.UNDERLINE}Цели:{Color.END}")
            for obj, details in quest.objectives.items():
                progress = details["current"]
                target = details["count"]
                completion = "✓" if obj in quest.completed_objectives else " "
                print(f"  [{completion}] {obj}: {progress}/{target}")
    
    # ОПТИМИЗАЦИЯ: объединение методов исследования
    def explore_location(self, location: Location):
        """Исследование локации"""
        while True:
            self.clear_screen()
            self.print_header(f"ИССЛЕДОВАНИЕ: {location.name}")
            
            print(f"{Color.CYAN}{location.description}{Color.END}")
            print(f"\nТип: {location.type.value}")
            print(f"Уровень сложности: {location.level_range[0]}-{location.level_range[1]}")
            
            # ИСПРАВЛЕНИЕ: показываем реальное количество врагов
            if location.cleared:
                print(f"{Color.GREEN}✓ Локация очищена{Color.END}")
            elif not location.enemies:
                print(f"{Color.YELLOW}○ Врагов нет{Color.END}")
            
            if location.enemies:
                print(f"\n{Color.RED}Вы обнаружили врагов:{Color.END}")
                # Показываем до 7 врагов (было 5)
                for i, enemy in enumerate(location.enemies[:7], 1):
                    health_percent = (enemy.health / enemy.max_health) * 100
                    health_color = Color.GREEN if health_percent > 50 else Color.YELLOW if health_percent > 20 else Color.RED
                    print(f"  {i}. {enemy.name} ({health_color}❤ {enemy.health}/{enemy.max_health}{Color.END})")
                
                # Показываем сколько всего врагов
                if len(location.enemies) > 7:
                    print(f"  ... и еще {len(location.enemies) - 7} врагов")
                else:
                    print(f"  Всего врагов: {len(location.enemies)}")
            
            if random.random() < location.special_event_chance:
                event = location.add_special_event()
                print(f"\n{Color.PURPLE}✨ {event}{Color.END}")
            
            print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
            
            options = []
            option_map = {}
            option_index = 1
            
            option_map[option_index] = ("Исследовать дальше", self.explore_further, [location])
            options.append((str(option_index), "Исследовать дальше"))
            option_index += 1
            
            if location.enemies:
                option_map[option_index] = ("Сражаться с врагами", self.start_battle, [location])
                options.append((str(option_index), "Сражаться с врагами"))
                option_index += 1
            
            option_map[option_index] = ("Искать сокровища", self.search_treasure, [location])
            options.append((str(option_index), "Искать сокровища"))
            option_index += 1
            
            if location.type == LocationType.TOWN:
                if location.has_tavern:
                    option_map[option_index] = ("Посетить таверну", self.visit_tavern, [])
                    options.append((str(option_index), "Посетить таверну"))
                    option_index += 1
                if location.has_shop:
                    option_map[option_index] = ("Посетить магазин", self.visit_shop, [])
                    options.append((str(option_index), "Посетить магазин"))
                    option_index += 1
                if location.has_bordello:
                    option_map[option_index] = ("Посетить бордель", self.visit_bordello, [])
                    options.append((str(option_index), "Посетить бордель"))
                    option_index += 1
                option_map[option_index] = ("Поговорить с жителями", self.talk_to_npcs, [])
                options.append((str(option_index), "Поговорить с жителями"))
                option_index += 1
            
            option_map[option_index] = ("Осмотреть местность", self.examine_area, [])
            options.append((str(option_index), "Осмотреть местность"))
            option_index += 1
            
            option_map[option_index] = ("Вернуться", None, [])
            options.append((str(option_index), "Вернуться"))
            
            for key, desc in options:
                print(f"{key}. {desc}")
            
            choice = self.get_choice(1, len(options))
            
            if choice < len(options):
                _, func, args = option_map[choice]
                if func:
                    func(*args)
                    if self.player and self.player.health <= 0:
                        return
            else:
                break
    
    def explore_further(self, location: Location):
        """Дальнейшее исследование локации"""
        self.clear_screen()
        self.print_header(f"ГЛУБЖЕ В {location.name}")
        
        events = [
            "Вы нашли заброшенную хижину",
            "Вы обнаружили древние надписи на стенах",
            "Вы наткнулись на водопад",
            "Вы нашли тайную тропу",
            "Вы обнаружили следы чудовища",
            "Вы нашли странный алтарь",
            "Вы нашли источник чистой воды",
            "Вы обнаружили гнездо редкой птицы",
            "Вы нашли вход в пещеру",
            "Вы обнаружили поляну с редкими растениями"
        ]
        
        event = random.choice(events)
        print(f"{Color.YELLOW}{event}{Color.END}")
        
        luck_bonus = self.player.get_stat_bonus("luck") * 0.05
        find_chance = 0.4 + luck_bonus
        
        if random.random() < find_chance:
            found_items = []
            
            gold_found = random.randint(5, 50) + (self.player.level * 2)
            self.player.gold += gold_found
            found_items.append(f"{Color.YELLOW}{gold_found} золота{Color.END}")
            
            if random.random() < 0.3:
                available_items = [item for item in self.items_db.values() 
                                  if item.value <= 100 + (self.player.level * 20)]
                if available_items:
                    item = random.choice(available_items).copy()
                    self.player.add_item(item)
                    found_items.append(f"{item.get_colored_name()}")
            
            if found_items:
                print(f"{Color.GREEN}Вы нашли: {', '.join(found_items)}!{Color.END}")
        
        encounter_chance = 0.3 - (self.player.get_stat_bonus("dexterity") * 0.02)
        if random.random() < encounter_chance and location.enemies:
            print(f"\n{Color.RED}Вас атаковал враг!{Color.END}")
            time.sleep(1)
            self.start_battle(location)
        else:
            if random.random() < 0.2 and self.player.quests:
                print(f"\n{Color.CYAN}Вы нашли подсказку, связанную с одним из ваших квестов!{Color.END}")
            
            input(f"\n{Color.WHITE}Нажмите Enter, чтобы продолжить...{Color.END}")
    
    def search_treasure(self, location: Location):
        """Поиск сокровищ"""
        self.clear_screen()
        self.print_header("ПОИСК СОКРОВИЩ")
        
        print(f"{Color.YELLOW}Вы тщательно обыскиваете местность...{Color.END}")
        time.sleep(1)
        
        dexterity_bonus = self.player.get_stat_bonus("dexterity") * 0.03
        luck_bonus = self.player.get_stat_bonus("luck") * 0.05
        success_chance = 0.5 + dexterity_bonus + luck_bonus
        
        difficulty_penalty = {
            Difficulty.EASY: 0.1,
            Difficulty.NORMAL: 0,
            Difficulty.HARD: -0.1,
            Difficulty.INSANE: -0.2
        }.get(self.player.difficulty, 0)
        
        success_chance += difficulty_penalty
        
        if random.random() < success_chance:
            treasures = [
                ("небольшой сундук с золотом", "gold", (20, 50)),
                ("магический артефакт", "item", None),
                ("древний свиток", "scroll", None),
                ("целый клад", "gold", (55, 120)),
                ("сундук с драгоценностями", "gold", (60, 100)),
                ("зачарованный предмет", "enchanted_item", None),
                ("тайник с ресурсами", "resources", None)
            ]
            
            treasure = random.choice(treasures)
            name, treasure_type, gold_range = treasure
            
            print(f"{Color.GREEN}Вы нашли {name}!{Color.END}")
            
            if treasure_type == "gold":
                gold = random.randint(gold_range[0], gold_range[1])
                gold += self.player.level * 5
                self.player.gold += gold
                print(f"{Color.YELLOW}+{gold} золота{Color.END}")
                self.player.check_achievement("collect_gold", gold)
            
            elif treasure_type == "item":
                available_items = [item for item in self.items_db.values() 
                                  if item.value <= 100 + (self.player.level * 20)]
                if available_items:
                    item = random.choice(available_items).copy()
                    self.player.add_item(item)
                    print(f"{Color.CYAN}Вы нашли: {item.get_colored_name()}{Color.END}")
            
            elif treasure_type == "scroll":
                scrolls = [item for item in self.items_db.values() 
                          if item.item_type == ItemType.SCROLL]
                if scrolls:
                    scroll = random.choice(scrolls).copy()
                    self.player.add_item(scroll)
                    print(f"{Color.BLUE}Вы нашли: {scroll.get_colored_name()}{Color.END}")
            
            elif treasure_type == "enchanted_item":
                available_items = [item for item in self.items_db.values() 
                                  if item.item_type in [ItemType.WEAPON, ItemType.ARMOR, 
                                                       ItemType.HELMET, ItemType.GLOVES, ItemType.BOOTS]
                                  and item.value <= 200]
                if available_items:
                    item = random.choice(available_items).copy()
                    item.damage = int(item.damage * 1.5) if item.damage > 0 else 0
                    item.defense = int(item.defense * 1.5) if item.defense > 0 else 0
                    item.value = int(item.value * 2)
                    item.rarity = "Эпический"
                    item.name = f"Зачарованный {item.name}"
                    self.player.add_item(item)
                    print(f"{Color.PURPLE}Вы нашли: {item.get_colored_name()}{Color.END}")
            
            elif treasure_type == "resources":
                resources = ["Железная руда", "Магический кристалл", "Кожа", "Ткань", "Дерево"]
                resource = random.choice(resources)
                resource_item = Item(resource, ItemType.MATERIAL, 
                                    value=random.randint(10, 50),
                                    description=f"Ценный ресурс: {resource}")
                self.player.add_item(resource_item)
                print(f"{Color.GREEN}Вы нашли: {resource}{Color.END}")
        else:
            failures = [
                "Вы наткнулись на ловушку и получили урон!",
                "Вы ничего не нашли",
                "Вас заметили враги!",
                "Сокровище оказалось фальшивым",
                "Вы потревожили гнездо опасных существ",
                "Ловушка оглушила вас на несколько секунд",
                "Вы чуть не провалились в яму"
            ]
            
            failure = random.choice(failures)
            print(f"{Color.RED}{failure}{Color.END}")
            
            if "урон" in failure:
                damage = random.randint(5, 25)
                self.player.take_damage(damage)
                print(f"{Color.RED}-{damage} здоровья{Color.END}")
            
            if "заметили" in failure or "потревожили" in failure:
                if location.enemies:
                    time.sleep(1)
                    self.start_battle(location)
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы продолжить...{Color.END}")
    
    def talk_to_npcs(self):
        """Разговор с NPC"""
        self.clear_screen()
        self.print_header("ОБЩЕНИЕ С ЖИТЕЛЯМИ")
        
        npcs = [
            ("Старый солдат", "Видел я много битв... Дракон - это серьезно. Готовься как следует."),
            ("Торговец", "Нужны припасы? У меня всегда есть что предложить!"),
            ("Крестьянин", "Урожай в этом году плохой... Монстры совсем распоясались."),
            ("Мудрец", "Истинная сила не в оружии, а в знаниях. Учись, и ты победишь."),
            ("Странник", "Я видел дракона... Он огромен. Будь осторожен."),
            ("Эльфийский следопыт", "Лес полон опасностей, но и секретов тоже."),
            ("Гном-кузнец", "Хорошее оружие - половина победы. Приходи в кузницу!"),
            ("Жрица", "Боги наблюдают за тобой. Не подведи их.")
        ]
        
        npc = random.choice(npcs)
        name, dialogue = npc
        
        print(f"{Color.YELLOW}{name}:{Color.END}")
        print(f'"{dialogue}"')
        
        if random.random() < 0.3:
            print(f"\n{Color.GREEN}{name} дает вам полезный совет!{Color.END}")
            
            if random.random() < 0.5:
                tips = [
                    "Не забывайте использовать зелья в бою",
                    "Исследуйте каждую локацию тщательно",
                    "Прокачивайте характеристики равномерно",
                    "Экипируйте лучшее оружие и броню",
                    "Выполняйте квесты для получения опыта"
                ]
                print(f"Совет: {random.choice(tips)}")
            else:
                enemy_info = [
                    "Гоблины слабы, но атакуют толпой",
                    "Волки быстры, но имеют мало здоровья",
                    "Тролли медлительны, но очень сильны",
                    "Драконы используют огненное дыхание",
                    "Некроманты могут воскрешать мертвых"
                ]
                print(f"Знание о врагах: {random.choice(enemy_info)}")
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы продолжить...{Color.END}")
    
    # ОПТИМИЗАЦИЯ: упрощенный метод для магазина
    def visit_shop(self):
        """Посещение магазина"""
        while True:
            self.clear_screen()
            self.print_header("МАГАЗИН 'ВСЕ ДЛЯ ПРИКЛЮЧЕНИЙ'")
            
            print(f"{Color.YELLOW}На полках магазина множество странных и полезных вещей.{Color.END}")
            print(f"Ваше золото: {Color.YELLOW}{self.player.gold}{Color.END}")
            print(f"Ваш класс: {Color.CYAN}{self.player.character_class.value}{Color.END}")
            print(f"Ваш уровень: {Color.GREEN}{self.player.level}{Color.END}")
            
            current_location = self.game_world.get(self.player.location)
            location_min_level = current_location.level_range[0] if current_location else 1
            
            min_item_level = max(1, min(self.player.level - 2, location_min_level))
            max_item_level = self.player.level + 2
            
            print(f"Доступные уровни предметов: {min_item_level}-{max_item_level}")
            
            shop_items = []
            for item in self.items_db.values():
                if hasattr(item, 'character_classes') and item.character_classes:
                    if self.player.character_class not in item.character_classes:
                        continue
                
                if item.required_level < min_item_level or item.required_level > max_item_level:
                    continue
                
                if item.value <= 100 + (self.player.level * 20):
                    shop_items.append(item.copy())
            
            shop_items.sort(key=lambda x: (x.item_type.value, x.required_level, x.value))
            
            items_by_type = {}
            for item in shop_items:
                if item.item_type not in items_by_type:
                    items_by_type[item.item_type] = []
                items_by_type[item.item_type].append(item)
            
            item_index = 1
            item_map = {}
            
            type_order = [
                ItemType.WEAPON, ItemType.ARMOR, ItemType.HELMET,
                ItemType.GLOVES, ItemType.BOOTS, ItemType.RING,
                ItemType.AMULET, ItemType.POTION, ItemType.SCROLL
            ]
            
            for item_type in type_order:
                if item_type in items_by_type and items_by_type[item_type]:
                    print(f"\n{Color.BOLD}{item_type.value}:{Color.END}")
                    
                    for item in items_by_type[item_type]:
                        level_color = Color.GREEN if item.required_level <= self.player.level else Color.YELLOW
                        
                        class_info = ""
                        if hasattr(item, 'character_classes') and item.character_classes:
                            classes = [c.value for c in item.character_classes]
                            if len(classes) < 4:
                                class_info = f" [{Color.CYAN}Для: {', '.join(classes)}{Color.END}]"
                        
                        print(f"  {item_index}. {item.get_colored_name()}")
                        print(f"     {item.description}")
                        print(f"     Требует уровень: {level_color}{item.required_level}{Color.END}{class_info}")
                        
                        stats = []
                        if item.damage > 0:
                            stats.append(f"Урон: {item.damage}")
                        if item.defense > 0:
                            stats.append(f"Защита: {item.defense}")
                        if item.health > 0:
                            stats.append(f"Здоровье: +{item.health}")
                        if item.mana > 0:
                            stats.append(f"Мана: +{item.mana}")
                        
                        if stats:
                            print(f"     {', '.join(stats)}")
                        
                        # Показываем специальный эффект оружия
                        if item.special_effect:
                            effect_names = {
                                "fire_damage": "Огненный урон",
                                "mana_steal": "Кража маны",
                                "critical_chance": "Шанс крита",
                                "poison": "Яд",
                                "life_steal": "Кража здоровья",
                                "stun_chance": "Оглушение",
                                "armor_penetration": "Пробитие брони"
                            }
                            effect_name = effect_names.get(item.special_effect, item.special_effect)
                            print(f"     {Color.CYAN}Эффект: {effect_name}{Color.END}")
                        
                        print(f"     Цена: {Color.YELLOW}{item.value} золота{Color.END}")
                        item_map[item_index] = item
                        item_index += 1
            
            if item_index == 1:
                print(f"\n{Color.YELLOW}В магазине нет подходящих для вас предметов.{Color.END}")
                print(f"Возможно, ваш уровень слишком низок для этой локации.")
                print(f"Текущая локация: {self.player.location} (уровень: {location_min_level}+)")
            
            print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
            print(f"{item_index}. Продать предметы")
            print(f"{item_index + 1}. Починить экипировку")
            print(f"{item_index + 2}. Уйти")
            
            choice = self.get_choice(1, item_index + 2)
            
            if choice < item_index:
                item = item_map[choice]
                
                if item.required_level > self.player.level:
                    print(f"{Color.RED}Ваш уровень слишком низок для этого предмета!{Color.END}")
                    print(f"Ваш уровень: {self.player.level}, требуется: {item.required_level}")
                    time.sleep(2)
                    continue
                
                if hasattr(item, 'character_classes') and item.character_classes:
                    if self.player.character_class not in item.character_classes:
                        print(f"{Color.RED}Этот предмет не подходит для вашего класса!{Color.END}")
                        classes = [c.value for c in item.character_classes]
                        print(f"Предмет предназначен для: {', '.join(classes)}")
                        time.sleep(2)
                        continue
                
                if self.player.gold >= item.value:
                    confirm = input(f"Купить {item.name} за {item.value} золота? (y/n): ")
                    if confirm.lower() == 'y':
                        self.player.gold -= item.value
                        bought_item = item.copy()
                        self.player.add_item(bought_item)
                        print(f"{Color.GREEN}Вы купили {item.name}!{Color.END}")
                        time.sleep(1)
                else:
                    print(f"{Color.RED}У вас недостаточно золота{Color.END}")
                    time.sleep(1)
            
            elif choice == item_index:
                self.sell_items()
            
            elif choice == item_index + 1:
                self.repair_equipment()
            
            elif choice == item_index + 2:
                break
    
    def sell_items(self):
        """Продажа предметов"""
        self.clear_screen()
        self.print_header("ПРОДАЖА ПРЕДМЕТОВ")
        
        if not self.player.inventory:
            print(f"{Color.YELLOW}У вас нет предметов для продажи{Color.END}")
            time.sleep(1)
            return
        
        print(f"Ваше золото: {Color.YELLOW}{self.player.gold}{Color.END}")
        print(f"\n{Color.BOLD}ВАШИ ПРЕДМЕТЫ:{Color.END}")
        
        for i, item in enumerate(self.player.inventory, 1):
            sell_price = max(1, item.value // 2)
            luck_bonus = self.player.get_stat_bonus("luck") * 0.01
            sell_price = int(sell_price * (1 + luck_bonus))
            
            class_info = ""
            if hasattr(item, 'character_classes') and item.character_classes:
                classes = [c.value for c in item.character_classes]
                if len(classes) < 4:
                    class_info = f" [Для: {', '.join(classes)}]"
            
            print(f"{i}. {item.get_colored_name()}{class_info} - {sell_price} золота")
        
        print(f"\n{Color.WHITE}Выберите предмет для продажи (0 - отмена):{Color.END}")
        choice = self.get_choice(0, len(self.player.inventory))
        
        if choice > 0:
            item = self.player.inventory[choice - 1]
            sell_price = max(1, item.value // 2)
            luck_bonus = self.player.get_stat_bonus("luck") * 0.01
            sell_price = int(sell_price * (1 + luck_bonus))
            
            print(f"\n{Color.YELLOW}Продать {item.name} за {sell_price} золота?{Color.END}")
            print("1. Да, продать")
            print("2. Нет, оставить")
            
            confirm = self.get_choice(1, 2)
            
            if confirm == 1:
                self.player.gold += sell_price
                self.player.remove_item(item)
                print(f"{Color.GREEN}Предмет продан!{Color.END}")
                time.sleep(1)
    
    def repair_equipment(self):
        """Ремонт экипировки"""
        self.clear_screen()
        self.print_header("РЕМОНТ ЭКИПИРОВКИ")
        
        damaged_items = []
        for slot, item in self.player.equipped.items():
            if item and item.durability < item.max_durability:
                damaged_items.append((slot, item))
        
        if not damaged_items:
            print(f"{Color.YELLOW}Вся ваша экипировка в отличном состоянии!{Color.END}")
            time.sleep(1)
            return
        
        print(f"Ваше золото: {Color.YELLOW}{self.player.gold}{Color.END}")
        print(f"\n{Color.BOLD}ПОВРЕЖДЕННАЯ ЭКИПИРОВКА:{Color.END}")
        
        for i, (slot, item) in enumerate(damaged_items, 1):
            slot_name = {
                "weapon": "Оружие",
                "armor": "Броня",
                "helmet": "Шлем",
                "gloves": "Перчатки",
                "boots": "Сапоги"
            }.get(slot, slot)
            
            repair_cost = int((item.max_durability - item.durability) * 0.5)
            print(f"{i}. {slot_name}: {item.get_colored_name()}")
            print(f"   Стоимость ремонта: {repair_cost} золота")
        
        print(f"\n{Color.WHITE}Выберите предмет для ремонта (0 - отмена):{Color.END}")
        choice = self.get_choice(0, len(damaged_items))
        
        if choice > 0:
            slot, item = damaged_items[choice - 1]
            repair_cost = int((item.max_durability - item.durability) * 0.5)
            
            if self.player.gold >= repair_cost:
                confirm = input(f"Отремонтировать {item.name} за {repair_cost} золота? (y/n): ")
                if confirm.lower() == 'y':
                    self.player.gold -= repair_cost
                    item.repair()
                    print(f"{Color.GREEN}{item.name} полностью отремонтирован!{Color.END}")
            else:
                print(f"{Color.RED}У вас недостаточно золота{Color.END}")
            
            time.sleep(1)
    
    def start_battle(self, location: Location):
        """Начало битвы"""
        if not location.enemies:
            print(f"{Color.YELLOW}В этой локации нет врагов{Color.END}")
            time.sleep(1)
            return
        
        self.clear_screen()
        self.print_header("ВЫБОР ПРОТИВНИКА")
        
        print(f"{Color.RED}Выберите противника:{Color.END}")
        
        sorted_enemies = sorted(location.enemies, key=lambda x: x.level)
        
        for i, enemy in enumerate(sorted_enemies[:7], 1):  # Увеличили до 7 врагов
            health_percent = (enemy.health / enemy.max_health) * 100
            health_color = Color.GREEN if health_percent > 50 else Color.YELLOW if health_percent > 20 else Color.RED
            
            difficulty_indicator = ""
            if enemy.level > self.player.level + 2:
                difficulty_indicator = f" {Color.RED}(Очень сложно){Color.END}"
            elif enemy.level > self.player.level:
                difficulty_indicator = f" {Color.YELLOW}(Сложно){Color.END}"
            elif enemy.level < self.player.level - 2:
                difficulty_indicator = f" {Color.GREEN}(Легко){Color.END}"
            
            print(f"{i}. {enemy.name}{difficulty_indicator}")
            print(f"   Здоровье: {health_color}{enemy.health}/{enemy.max_health}{Color.END}")
            print(f"   Урон: {enemy.damage}, Защита: {enemy.defense}")
            
            if enemy.special_abilities:
                print(f"   Способности: {', '.join(enemy.special_abilities)}")
        
        print(f"\n{len(sorted_enemies[:7]) + 1}. Сражаться со случайным врагом")
        print(f"{len(sorted_enemies[:7]) + 2}. Вернуться")
        
        choice = self.get_choice(1, len(sorted_enemies[:7]) + 2)
        
        if choice == len(sorted_enemies[:7]) + 1:
            enemy = random.choice(location.enemies)
            self.battle(enemy, location)
        elif choice <= len(sorted_enemies[:7]):
            enemy = sorted_enemies[choice - 1]
            self.battle(enemy, location)
    
    def battle(self, enemy: Enemy, location: Location):
        """Битва с врагом - ДОБАВЛЕН ФУНКЦИОНАЛ СПЕЦИАЛЬНЫХ ЭФФЕКТОВ"""
        self.current_battle = {
            "enemy": enemy,
            "location": location,
            "player_turn": True,
            "round": 1
        }
        
        print(f"\n{Color.RED}Начинается битва с {enemy.name}!{Color.END}")
        time.sleep(1)
        
        while enemy.health > 0 and self.player.health > 0:
            self.clear_screen()
            self.print_header(f"БИТВА - РАУНД {self.current_battle['round']}")
            
            print(f"{Color.GREEN}{self.player.name} (Ур.{self.player.level}){Color.END}")
            health_bar = self.create_bar(self.player.health, self.player.max_health, 30)
            mana_bar = self.create_bar(self.player.mana, self.player.max_mana, 30, Color.BLUE, Color.BLUE, Color.PURPLE)
            print(f"Здоровье: {health_bar}")
            print(f"Мана:     {mana_bar}")
            
            print(f"\n{Color.RED}{enemy.name} (Ур.{enemy.level}){Color.END}")
            enemy_health_bar = self.create_bar(enemy.health, enemy.max_health, 30)
            print(f"Здоровье: {enemy_health_bar}")
            
            if enemy.special_abilities:
                print(f"Способности: {', '.join(enemy.special_abilities)}")
            
            print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
            
            if self.current_battle["player_turn"]:
                print(f"{Color.YELLOW}Ваш ход:{Color.END}")
                print("1. Атаковать")
                print("2. Использовать предмет")
                print("3. Использовать умение")
                print("4. Защищаться (увеличивает защиту на 1 ход)")
                print("5. Попытаться убежать")
                
                choice = self.get_choice(1, 5)
                
                if choice == 1:
                    # ИСПРАВЛЕНИЕ: передаем врага в атаку для применения специальных эффектов
                    damage, message = self.player.attack(enemy)
                    if damage > 0:
                        enemy.health -= damage
                        print(f"\n{message}")
                        print(f"{Color.GREEN}Вы нанесли {damage} урона!{Color.END}")
                    else:
                        print(f"\n{message}")
                    self.current_battle["player_turn"] = False
                
                elif choice == 2:
                    self.use_item_in_battle()
                    self.current_battle["player_turn"] = False
                
                elif choice == 3:
                    self.use_skill_in_battle(enemy)
                    self.current_battle["player_turn"] = False
                
                elif choice == 4:
                    defense_bonus = self.player.get_stat_bonus("constitution") // 2
                    print(f"\n{Color.GREEN}Вы принимаете защитную стойку! (+{defense_bonus} к защите на 1 ход){Color.END}")
                    self.current_battle["player_turn"] = False
                
                elif choice == 5:
                    escape_chance = 0.5 + self.player.get_stat_bonus("dexterity") * 0.1
                    if random.random() < escape_chance:
                        print(f"\n{Color.GREEN}Вы успешно сбежали!{Color.END}")
                        time.sleep(1)
                        return
                    else:
                        print(f"\n{Color.RED}Вам не удалось сбежать!{Color.END}")
                        self.current_battle["player_turn"] = False
                
            else:
                print(f"\n{Color.YELLOW}Ход противника...{Color.END}")
                time.sleep(1)
                
                if enemy.special_abilities and random.random() < 0.3:
                    special_damage, special_message = enemy.use_special_ability()
                    if special_message:
                        print(f"\n{special_message}")
                    
                    if special_damage > 0:
                        is_dead = self.player.take_damage(special_damage)
                        print(f"{enemy.name} наносит {special_damage} урона!")
                else:
                    enemy_damage = random.randint(
                        max(1, enemy.damage - 2),
                        enemy.damage + 2
                    )
                    
                    is_dead = self.player.take_damage(enemy_damage)
                    print(f"{enemy.name} атакует и наносит {enemy_damage} урона!")
                
                if is_dead:
                    print(f"\n{Color.RED}Вы погибли!{Color.END}")
                    self.game_over()
                    return
                
                self.current_battle["player_turn"] = True
                self.current_battle["round"] += 1
            
            time.sleep(1.5)
        
        if enemy.health <= 0:
            self.victory(enemy, location)
        elif self.player.health <= 0:
            self.game_over()
    
    def use_item_in_battle(self):
        """Использовать предмет в бою"""
        self.clear_screen()
        self.print_header("ИСПОЛЬЗОВАНИЕ ПРЕДМЕТА В БОЮ")
        
        usable_items = []
        for item in self.player.inventory:
            if item.item_type == ItemType.POTION:
                usable_items.append(item)
            elif item.item_type == ItemType.SCROLL and item.name == "Свиток воскрешения":
                usable_items.append(item)
        
        if not usable_items:
            print(f"{Color.YELLOW}У вас нет предметов для использования в бою{Color.END}")
            time.sleep(1)
            return
        
        print(f"{Color.GREEN}Доступные предметы:{Color.END}")
        for i, item in enumerate(usable_items, 1):
            if item.item_type == ItemType.POTION:
                if item.health > 0:
                    print(f"{i}. {item.name} (+{item.health} здоровья)")
                elif item.mana > 0:
                    print(f"{i}. {item.name} (+{item.mana} маны)")
                else:
                    print(f"{i}. {item.name}")
            elif item.item_type == ItemType.SCROLL:
                print(f"{i}. {item.name}")
        
        print(f"\n{len(usable_items) + 1}. Отмена")
        
        choice = self.get_choice(1, len(usable_items) + 1)
        
        if choice <= len(usable_items):
            item = usable_items[choice - 1]
            self.use_item(item)
    
    def use_skill_in_battle(self, enemy: Enemy):
        """Использовать умение в бою"""
        self.clear_screen()
        self.print_header("ИСПОЛЬЗОВАНИЕ УМЕНИЯ")
        
        skills = {
            "Сильный удар": {"cost": 10, "damage_mult": 1.5, "class": CharacterClass.WARRIOR, "description": "Мощный удар, наносящий увеличенный урон"},
            "Огненный шар": {"cost": 20, "damage_mult": 2.0, "class": CharacterClass.MAGE, "description": "Шар огня, поджигающий врага"},
            "Стрела снайпера": {"cost": 15, "damage_mult": 1.8, "class": CharacterClass.ARCHER, "description": "Точный выстрел в уязвимое место"},
            "Скрытый удар": {"cost": 12, "damage_mult": 1.7, "class": CharacterClass.ROGUE, "description": "Внезапная атака из укрытия"},
            "Лечение": {"cost": 15, "heal": 30, "class": CharacterClass.MAGE, "description": "Восстанавливает здоровье"},
            "Уклонение": {"cost": 8, "dodge": 0.5, "class": CharacterClass.ROGUE, "description": "Увеличивает шанс уклонения"},
            "Берсерк": {"cost": 25, "damage_mult": 2.5, "self_damage": 10, "class": CharacterClass.WARRIOR, "description": "Мощная атака ценой здоровья"}
        }
        
        available_skills = []
        for skill_name, skill_info in skills.items():
            if skill_info["class"] == self.player.character_class:
                available_skills.append((skill_name, skill_info))
        
        if not available_skills:
            print(f"{Color.YELLOW}У вас нет доступных умений{Color.END}")
            time.sleep(1)
            return
        
        print(f"{Color.CYAN}Доступные умения:{Color.END}")
        for i, (skill_name, skill_info) in enumerate(available_skills, 1):
            print(f"{i}. {skill_name} (Стоимость: {skill_info['cost']} маны)")
            print(f"   {skill_info['description']}")
        
        print(f"\n{len(available_skills) + 1}. Отмена")
        
        choice = self.get_choice(1, len(available_skills) + 1)
        
        if choice <= len(available_skills):
            skill_name, skill_info = available_skills[choice - 1]
            
            if self.player.mana >= skill_info["cost"]:
                self.player.mana -= skill_info["cost"]
                
                if "damage_mult" in skill_info:
                    base_damage = self.player.stats["strength"] // 2
                    if self.player.equipped["weapon"]:
                        base_damage += self.player.equipped["weapon"].damage
                    
                    damage = int(base_damage * skill_info["damage_mult"])
                    enemy.health -= damage
                    
                    print(f"\n{Color.GREEN}Вы используете {skill_name}!{Color.END}")
                    print(f"{Color.GREEN}Вы нанесли {damage} урона!{Color.END}")
                    
                    if skill_name == "Берсерк" and "self_damage" in skill_info:
                        self.player.health -= skill_info["self_damage"]
                        print(f"{Color.RED}Вы теряете {skill_info['self_damage']} здоровья!{Color.END}")
                
                elif "heal" in skill_info:
                    self.player.heal(skill_info["heal"])
                    print(f"\n{Color.GREEN}Вы используете {skill_name}!{Color.END}")
                    print(f"{Color.GREEN}Вы восстановили {skill_info['heal']} здоровья!{Color.END}")
                
                elif "dodge" in skill_info:
                    print(f"\n{Color.GREEN}Вы используете {skill_name}!{Color.END}")
                    print(f"{Color.GREEN}Ваш шанс уклонения увеличен!{Color.END}")
            else:
                print(f"{Color.RED}Недостаточно маны!{Color.END}")
            
            time.sleep(1.5)
    
    def victory(self, enemy: Enemy, location: Location):
        """Победа над врагом"""
        self.clear_screen()
        self.print_header("ПОБЕДА!")
        
        xp_gained = enemy.xp_reward
        gold_gained = enemy.gold_reward
        
        print(f"{Color.GREEN}Вы победили {enemy.name}!{Color.END}")
        print(f"\n{Color.YELLOW}НАГРАДЫ:{Color.END}")
        print(f"+{xp_gained} опыта")
        print(f"+{gold_gained} золота")
        
        leveled_up = self.player.gain_xp(xp_gained)
        self.player.gold += gold_gained
        
        enemy_type_name = enemy.type.value
        self.player.killed_enemies[enemy_type_name] = \
            self.player.killed_enemies.get(enemy_type_name, 0) + 1
        
        self.player.check_achievement("kill_enemy", 1)
        
        if enemy_type_name == "Дракон":
            self.player.check_achievement("kill_dragon", 1)
        elif enemy_type_name == "Слизень":
            self.player.check_achievement("kill_slime", 1)
        
        for quest in self.player.quests:
            if quest.status == QuestStatus.IN_PROGRESS:
                if enemy_type_name in quest.objectives:
                    completed = quest.update_objective(enemy_type_name)
                    if completed:
                        self.complete_quest(quest)
                else:
                    for obj in quest.objectives:
                        if "убить" in obj.lower() and enemy_type_name.lower() in obj.lower():
                            completed = quest.update_objective(obj)
                            if completed:
                                self.complete_quest(quest)
                            break
        
        loot_chance = enemy.loot_chance + (self.player.get_stat_bonus("luck") * 0.05)
        if random.random() < loot_chance:
            loot_pool = []
            
            for item_name, item in self.items_db.items():
                if item.value <= enemy.level * 25:
                    loot_pool.append(item)
            
            if loot_pool:
                num_loot = random.randint(1, min(3, enemy.level // 5 + 1))
                for _ in range(num_loot):
                    if random.random() < 0.7:
                        loot = random.choice(loot_pool).copy()
                        self.player.add_item(loot)
                        print(f"\n{Color.CYAN}Вы нашли: {loot.get_colored_name()}{Color.END}")
        
        if leveled_up:
            print(f"\n{Color.YELLOW}ПОЗДРАВЛЯЕМ! Вы достигли {self.player.level} уровня!{Color.END}")
        
        if enemy in location.enemies:
            location.enemies.remove(enemy)
        
        if not location.enemies:
            location.cleared = True
            print(f"\n{Color.GREEN}Локация '{location.name}' очищена!{Color.END}")
        
        if not location.enemies and location.respawn_timer >= 3:
            location.generate_enemies()
            location.cleared = False
            print(f"{Color.YELLOW}В локации появились новые враги.{Color.END}")
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы продолжить...{Color.END}")
    
    def complete_quest(self, quest: Quest):
        """Завершение квеста"""
        print(f"\n{Color.GREEN}✧ ✧ ✧ КВЕСТ ЗАВЕРШЕН: {quest.name} ✧ ✧ ✧{Color.END}")
        print(f"Награда: {quest.reward_xp} опыта, {quest.reward_gold} золота")
        
        self.player.gain_xp(quest.reward_xp)
        self.player.gold += quest.reward_gold
        
        if quest.reward_items:
            print(f"\n{Color.YELLOW}Дополнительные награды:{Color.END}")
            for item in quest.reward_items:
                item_copy = item.copy()
                self.player.add_item(item_copy)
                print(f"  - {item_copy.get_colored_name()}")
        
        quest.status = QuestStatus.COMPLETED
        self.player.check_achievement("complete_quest", 1)
        
        if quest.name == "Угроза дракона":
            self.player.check_achievement("complete_game", 1)
            print(f"\n{Color.YELLOW}✧ ✧ ✧ ПОБЕДА В ИГРЕ! ✧ ✧ ✧{Color.END}")
            print("Вы победили дракона и спасли королевство!")
            print("Игра завершена, но вы можете продолжать исследовать мир.")
        
        time.sleep(2)
    
    def game_over(self):
        """Конец игры"""
        self.clear_screen()
        self.print_header("ИГРА ОКОНЧЕНА")
        
        print(f"{Color.RED}Вы погибли в бою...{Color.END}")
        print(f"\n{Color.YELLOW}ИТОГИ ПРИКЛЮЧЕНИЯ:{Color.END}")
        print(f"Имя: {self.player.name}")
        print(f"Класс: {self.player.character_class.value}")
        print(f"Уровень: {self.player.level}")
        print(f"Золото: {self.player.gold}")
        print(f"Убито врагов: {sum(self.player.killed_enemies.values())}")
        
        completed_achievements = [a for a in self.player.achievements if a.completed]
        if completed_achievements:
            print(f"Достижений: {len(completed_achievements)}/{len(self.player.achievements)}")
            print(f"Лучшее достижение: {completed_achievements[-1].name}")
        
        if self.game_start_time:
            play_time = datetime.now() - self.game_start_time
            hours = play_time.seconds // 3600
            minutes = (play_time.seconds % 3600) // 60
            seconds = play_time.seconds % 60
            print(f"Время игры: {hours}ч {minutes}м {seconds}с")
        
        print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
        print("1. Начать заново")
        print("2. Загрузить сохранение")
        print("3. Выйти в главное меню")
        print("4. Выйти из игры")
        
        choice = self.get_choice(1, 4)
        
        if choice == 1:
            self.is_running = False
            new_game = Game()
            new_game.run()
        elif choice == 2:
            self.load_game_menu()
            if self.player:
                self.game_loop()
            else:
                self.main_menu()
        elif choice == 3:
            self.is_running = False
            self.player = None
            new_game = Game()
            new_game.main_menu()
        else:
            print(f"\n{Color.YELLOW}До свидания!{Color.END}")
            sys.exit(0)
    
    def examine_area(self):
        """Осмотр местности"""
        self.clear_screen()
        self.print_header("ОСМОТР МЕСТНОСТИ")
        
        observations = [
            "Вы замечаете следы недавнего боя",
            "Вы видите стаю птиц, улетающую на восток",
            "Вы чувствуете запах дыма",
            "Вы слышите отдаленный вой",
            "Вы находите обрывок карты",
            "Вы видите странные символы на деревьях",
            "Вы замечаете блеск вдалеке",
            "Вы чувствуете легкую дрожь земли"
        ]
        
        observation = random.choice(observations)
        print(f"{Color.CYAN}{observation}{Color.END}")
        
        if random.random() < 0.4:
            info_types = [
                "Вы понимаете, что здесь недавно прошла группа искателей приключений",
                "Вы определяете направление к ближайшему поселению",
                "Вы находите безопасный путь через эту местность",
                "Вы замечаете уязвимое место в обороне врагов"
            ]
            print(f"\n{Color.GREEN}{random.choice(info_types)}{Color.END}")
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы продолжить...{Color.END}")
    
    def visit_tavern(self):
        """Посещение таверны"""
        while True:
            self.clear_screen()
            self.print_header("ТАВЕРНА 'ПЬЯНЫЙ ГНОМ'")
            
            print(f"{Color.YELLOW}Вы входите в шумную таверну. Пахнет элем и жареным мясом.{Color.END}")
            print(f"За стойкой стоит улыбающийся бармен. В углу сидит группа искателей приключений.")
            
            print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
            print(f"Ваше золото: {Color.YELLOW}{self.player.gold}{Color.END}")
            print(f"Здоровье: {self.player.health}/{self.player.max_health}")
            print(f"Мана: {self.player.mana}/{self.player.max_mana}")
            
            print(f"\n{Color.BOLD}МЕНЮ:{Color.END}")
            print("1. Выпить эль (10 золота) - восстанавливает 30 здоровья")
            print("2. Заказать еду (20 золота) - восстанавливает 60 здоровья")
            print("3. Праздничный ужин (50 золта) - восстанавливает всё здоровье")
            print("4. Поговорить с барменом")
            print("5. Послушать сплетни")
            print("6. Сыграть в кости (ставка 10 золота)")
            print("7. Сыграть в Блэкджек (ставка 25 золота)")
            print("8. Арендовать комнату (30 золта) - полное восстановление")
            print("9. Уйти")
            
            choice = self.get_choice(1, 9)
            
            if choice == 1:
                if self.player.gold >= 10:
                    self.player.gold -= 10
                    self.player.heal(30)
                    print(f"{Color.GREEN}Вы выпили эль и восстановили 30 здоровья!{Color.END}")
                else:
                    print(f"{Color.RED}У вас недостаточно золота{Color.END}")
                time.sleep(1)
            
            elif choice == 2:
                if self.player.gold >= 20:
                    self.player.gold -= 20
                    self.player.heal(60)
                    print(f"{Color.GREEN}Вы поели и восстановили 60 здоровья!{Color.END}")
                else:
                    print(f"{Color.RED}У вас недостаточно золта{Color.END}")
                time.sleep(1)
            
            elif choice == 3:
                if self.player.gold >= 50:
                    self.player.gold -= 50
                    self.player.heal(self.player.max_health - self.player.health)
                    print(f"{Color.GREEN}Вы устроили себе праздник! Здоровье полностью восстановлено!{Color.END}")
                else:
                    print(f"{Color.RED}У вас недостаточно золта{Color.END}")
                time.sleep(1)
            
            elif choice == 4:
                print(f"\n{Color.YELLOW}Бармен:{Color.END} 'Приветствую, путник! Слушай, есть тут дело...'")
                
                available_quests = [q for q in self.quests_db.values() 
                                   if q.status == QuestStatus.NOT_STARTED 
                                   and q.required_level <= self.player.level
                                   and q.id not in [q.id for q in self.player.quests]]
                
                if available_quests:
                    quest = random.choice(available_quests)
                    print(f"\n{Color.CYAN}Бармен предлагает квест: {quest.name}{Color.END}")
                    print(f"{quest.description}")
                    print(f"Награда: {quest.reward_xp} опыта, {quest.reward_gold} золота")
                    
                    accept = input(f"\nПринять квест? (y/n): ")
                    if accept.lower() == 'y':
                        quest.status = QuestStatus.IN_PROGRESS
                        self.player.quests.append(quest)
                        print(f"{Color.GREEN}Квест принят!{Color.END}")
                else:
                    print(f"\n{Color.YELLOW}Бармен:{Color.END} 'Извини, сейчас нет подходящих дел. Возвращайся позже.'")
                
                time.sleep(2)
            
            elif choice == 5:
                rumors = [
                    "Говорят, в Темном лесу видели древнего волхва",
                    "В гоблинских пещеры нашли богатую жилу золота",
                    "Дракон сжег еще одну деревню на севере",
                    "Король объявил награду за голову предводителя орков",
                    "В Забытых руинах открылся портал в иной мир",
                    "Гномы нашли древний артефакт в горах",
                    "Ведьмы собираются на шабаш в болотах",
                    "Рыцари готовят поход на логово дракона"
                ]
                
                print(f"\n{Color.YELLOW}Вы подслушиваете разговоры:{Color.END}")
                for _ in range(3):
                    print(f"  - {random.choice(rumors)}")
                time.sleep(2)
            
            elif choice == 6:
                if self.player.gold >= 10:
                    print(f"\n{Color.YELLOW}Игра в кости!{Color.END}")
                    print("Бросаете 2 кубика. Если выпадет 7 или 11 - вы выигрываете!")
                    
                    input("Нажмите Enter, чтобы бросить кости...")
                    
                    dice1 = random.randint(1, 6)
                    dice2 = random.randint(1, 6)
                    total = dice1 + dice2
                    
                    print(f"Выпало: {dice1} + {dice2} = {total}")
                    
                    if total in [7, 11]:
                        win_amount = 20
                        self.player.gold += win_amount
                        print(f"{Color.GREEN}Вы выиграли {win_amount} золота!{Color.END}")
                    else:
                        self.player.gold -= 10
                        print(f"{Color.RED}Вы проиграли 10 золота.{Color.END}")
                else:
                    print(f"{Color.RED}У вас недостаточно золта для игры{Color.END}")
                time.sleep(2)
            
            elif choice == 7:
                self.play_blackjack()
            
            elif choice == 8:
                if self.player.gold >= 30:
                    self.player.gold -= 30
                    self.player.health = self.player.max_health
                    self.player.mana = self.player.max_mana
                    print(f"{Color.GREEN}Вы арендовали комнату и полностью восстановили здоровье и ману!{Color.END}")
                    
                    for slot in ["weapon", "armor", "helmet", "gloves", "boots"]:
                        if self.player.equipped[slot]:
                            self.player.equipped[slot].repair(50)
                    print(f"{Color.CYAN}Ваша экипировка частично отремонтирована.{Color.END}")
                else:
                    print(f"{Color.RED}У вас недостаточно золта{Color.END}")
                time.sleep(2)
            
            elif choice == 9:
                break
    
    def play_blackjack(self):
        """Игра в Блэкджек"""
        if self.player.gold < 25:
            print(f"{Color.RED}У вас недостаточно золота для игры в Блэкджек (нужно 25){Color.END}")
            time.sleep(1)
            return
        
        bet = 25
        print(f"\n{Color.YELLOW}Добро пожаловать в Блэкджек!{Color.END}")
        print(f"Ставка: {bet} золота")
        print("Цель: набрать 21 очко или ближе к 21, чем дилер")
        print("Туз = 11 или 1, картинки = 10")
        
        confirm = input(f"\nНачать игру? (y/n): ")
        if confirm.lower() != 'y':
            return
        
        deck = Deck()
        player_hand = []
        dealer_hand = []
        
        player_hand.append(deck.draw())
        player_hand.append(deck.draw())
        dealer_hand.append(deck.draw())
        dealer_hand.append(deck.draw())
        
        player_total = self.calculate_hand_value(player_hand)
        # Инициализируем dealer_total здесь
        dealer_total = self.calculate_hand_value(dealer_hand)
        
        while True:
            self.clear_screen()
            self.print_header("БЛЭКДЖЕК")
            
            print(f"Ставка: {Color.YELLOW}{bet} золота{Color.END}")
            print(f"\nВаши карты: {', '.join(str(card) for card in player_hand)}")
            print(f"Ваш счет: {player_total}")
            print(f"\nКарта дилера: {dealer_hand[0]} и [скрыта]")
            
            if player_total == 21:
                print(f"\n{Color.GREEN}БЛЭКДЖЕК!{Color.END}")
                break
            elif player_total > 21:
                print(f"\n{Color.RED}Перебор!{Color.END}")
                break
            
            print(f"\n{Color.YELLOW}Ваш ход:{Color.END}")
            print("1. Взять еще карту")
            print("2. Остановиться")
            
            choice = self.get_choice(1, 2)
            
            if choice == 1:
                new_card = deck.draw()
                player_hand.append(new_card)
                print(f"\nВы взяли: {new_card}")
                player_total = self.calculate_hand_value(player_hand)
                
                if player_total > 21:
                    print(f"\n{Color.RED}Перебор!{Color.END}")
                    break
            else:
                break
        
        # Ход дилера - только если у игрока не перебор
        if player_total <= 21:
            print(f"\n{Color.YELLOW}Ход дилера...{Color.END}")
            time.sleep(1)
            
            print(f"\nКарты дилера: {', '.join(str(card) for card in dealer_hand)}")
            print(f"Счет дилера: {dealer_total}")
            
            # Дилер берет карты пока счет < 17
            while dealer_total < 17:
                new_card = deck.draw()
                dealer_hand.append(new_card)
                dealer_total = self.calculate_hand_value(dealer_hand)
                print(f"Дилер берет: {new_card}")
                print(f"Новый счет дилера: {dealer_total}")
                time.sleep(1)
        
        # Определение победителя
        print(f"\n{Color.CYAN}{'='*50}{Color.END}")
        print(f"Ваш счет: {player_total}")
        
        # Обязательно выводим счет дилера, даже если был перебор
        if player_total <= 21:
            print(f"Счет дилера: {dealer_total}")
        else:
            # Если у игрока перебор, все равно показываем карты дилера
            dealer_total = self.calculate_hand_value(dealer_hand)
            print(f"Карты дилера: {', '.join(str(card) for card in dealer_hand)}")
            print(f"Счет дилера: {dealer_total}")
        
        if player_total > 21:
            result = "Вы проиграли!"
            winnings = -bet
        elif dealer_total > 21:
            result = "Дилер перебрал! Вы выиграли!"
            winnings = bet * 2
        elif player_total > dealer_total:
            result = "Вы выиграли!"
            winnings = bet * 2
        elif player_total < dealer_total:
            result = "Вы проиграли!"
            winnings = -bet
        else:
            result = "Ничья!"
            winnings = 0
        
        # Вывод результата и обновление золота
        if winnings > 0:
            print(f"{Color.GREEN}{result}{Color.END}")
            print(f"{Color.GREEN}Вы выиграли {winnings} золота!{Color.END}")
        elif winnings < 0:
            print(f"{Color.RED}{result}{Color.END}")
            print(f"{Color.RED}Вы проиграли {abs(winnings)} золота.{Color.END}")
        else:
            print(f"{Color.YELLOW}{result}{Color.END}")
            print("Ставка возвращена.")
        
        self.player.gold += winnings
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы продолжить...{Color.END}")
    
    def calculate_hand_value(self, hand: List[Card]) -> int:
        """Расчет значения руки в Блэкджеке"""
        total = 0
        aces = 0
        
        for card in hand:
            if card.rank == 'A':
                aces += 1
                total += 11
            else:
                total += card.value
        
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def visit_bordello(self):
        """Посещение борделя"""
        while True:
            self.clear_screen()
            self.print_header("РОСКОШНЫЙ БОРДЕЛЬ")
            
            print(f"{Color.PURPLE}Вы входите в роскошно обставленный бордель.{Color.END}")
            print(f"В воздухе витает аромат дорогих духов и слышится тихая музыка.")
            print(f"Хозяйка заведения встречает вас улыбкой.")
            
            print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
            print(f"Ваше золото: {Color.YELLOW}{self.player.gold}{Color.END}")
            print(f"Здоровье: {self.player.health}/{self.player.max_health}")
            print(f"Боевой дух: {self.player.morale}/100")
            
            available_girls = [girl for girl in self.bordello_girls if girl.available]
            unavailable_girls = [girl for girl in self.bordello_girls if not girl.available]
            
            print(f"\n{Color.BOLD}ДОСТУПНЫЕ ДЕВУШКИ:{Color.END}")
            if available_girls:
                for i, girl in enumerate(available_girls, 1):
                    print(f"\n{i}. {Color.PURPLE}{girl.name}{Color.END} - {girl.specialty}")
                    print(f"   Цена: {girl.price} золота")
                    print(f"   {girl.description}")
                    print(f"   Выносливость: {girl.stamina}/100")
            else:
                print(f"{Color.YELLOW}Все девушки отдыхают, приходите позже.{Color.END}")
            
            if unavailable_girls:
                print(f"\n{Color.BOLD}ОТДЫХАЮТ:{Color.END}")
                for girl in unavailable_girls[:3]:
                    print(f"   {girl.name} - восстановление...")
            
            print(f"\n{Color.BOLD}МЕНЮ:{Color.END}")
            print("1. Выбрать девушку")
            print("2. Поговорить с хозяйкой")
            print("3. Посмотреть специальные предложения")
            print("4. Отдохнуть в VIP-комнате (100 золота)")
            print("5. Уйти")
            
            choice = self.get_choice(1, 5)
            
            if choice == 1:
                if not available_girls:
                    print(f"{Color.YELLOW}Нет доступных девушек в данный момент.{Color.END}")
                    time.sleep(1)
                    continue
                
                print(f"\n{Color.WHITE}Выберите девушку:{Color.END}")
                for i, girl in enumerate(available_girls, 1):
                    print(f"{i}. {girl.name} - {girl.specialty} ({girl.price} золота)")
                
                girl_choice = self.get_choice(1, len(available_girls))
                selected_girl = available_girls[girl_choice - 1]
                
                if self.player.gold >= selected_girl.price:
                    print(f"\n{Color.PURPLE}Вы выбираете {selected_girl.name}...{Color.END}")
                    time.sleep(1)
                    
                    result, effects = selected_girl.provide_service()
                    print(f"\n{Color.CYAN}{result}{Color.END}")
                    
                    self.player.gold -= selected_girl.price
                    
                    if "health" in effects:
                        self.player.heal(effects["health"])
                        print(f"{Color.GREEN}+{effects['health']} здоровья{Color.END}")
                    
                    if "morale" in effects:
                        self.player.morale = min(100, self.player.morale + effects["morale"])
                        print(f"{Color.GREEN}+{effects['morale']} боевого духа{Color.END}")
                    
                    if "xp_bonus" in effects:
                        self.player.gain_xp(effects["xp_bonus"])
                        print(f"{Color.GREEN}+{effects['xp_bonus']} опыта{Color.END}")
                    
                    if "stamina_recovery" in effects:
                        self.player.stamina = min(100, self.player.stamina + effects["stamina_recovery"])
                        print(f"{Color.GREEN}+{effects['stamina_recovery']} выносливости{Color.END}")
                    
                    if "quest_hint" in effects and self.player.quests:
                        quest = random.choice(self.player.quests)
                        print(f"{Color.CYAN}Вы узнали полезную информацию о квесте '{quest.name}'{Color.END}")
                    
                    for quest in self.player.quests:
                        if quest.status == QuestStatus.IN_PROGRESS:
                            if "Бордель" in quest.objectives:
                                completed = quest.update_objective("Бордель")
                                if completed:
                                    self.complete_quest(quest)
                            elif "Посетить бордель" in quest.objectives:
                                completed = quest.update_objective("Посетить бордель")
                                if completed:
                                    self.complete_quest(quest)
                    
                else:
                    print(f"{Color.RED}У вас недостаточно золота{Color.END}")
                
                time.sleep(2)
            
            elif choice == 2:
                print(f"\n{Color.PURPLE}Хозяйка:{Color.END}")
                print("'Добро пожаловать в наше заведение, дорогой гость!'")
                print("'У нас только самые красивые и умелые девушки.'")
                print("'Если хочешь особых услуг - спрашивай у меня.'")
                
                if self.player.gold >= 200:
                    print(f"\n{Color.CYAN}'У меня есть для вас специальное предложение...'{Color.END}")
                    print("'За 200 золоток я могу организовать для вас вечеринку'")
                    
                    special = input("Устроить вечеринку? (y/n): ")
                    if special.lower() == 'y':
                        self.player.gold -= 200
                        print(f"\n{Color.PURPLE}Вечеринка удалась!{Color.END}")
                        self.player.heal(100)
                        self.player.morale = 100
                        self.player.stamina = 100
                        print(f"{Color.GREEN}Все характеристики полностью восстановлены!{Color.END}")
                
                time.sleep(2)
            
            elif choice == 3:
                print(f"\n{Color.BOLD}СПЕЦИАЛЬНЫЕ ПРЕДЛОЖЕНИЯ:{Color.END}")
                print("1. Ночной пакет (300 золота)")
                print("   - Полное восстановление всех характеристик")
                print("   - +50 к максимальному здоровью на 1 день")
                print("   - +20 к удаче на 1 день")
                
                print("\n2. Обучение у опытной куртизанки (150 золота)")
                print("   - +5 к харизме (увеличивает скидки в магазинах)")
                print("   - +10 к удаче на 3 дня")
                
                print("\n3. Массаж от двух девушек (120 золота)")
                print("   - +80 здоровья")
                print("   - +50 выносливости")
                print("   - Снятие всех негативных эффектов")
                
                special_choice = input(f"\nВыбрать предложение (1-3) или 0 для отмены: ")
                
                if special_choice in ['1', '2', '3']:
                    prices = {'1': 300, '2': 150, '3': 120}
                    price = prices[special_choice]
                    
                    if self.player.gold >= price:
                        self.player.gold -= price
                        
                        if special_choice == '1':
                            print(f"\n{Color.PURPLE}Ночной пакет активирован!{Color.END}")
                            self.player.health = self.player.max_health
                            self.player.mana = self.player.max_mana
                            self.player.morale = 100
                            self.player.stamina = 100
                            print(f"{Color.GREEN}Все характеристики восстановлены!{Color.END}")
                        
                        elif special_choice == '2':
                            print(f"\n{Color.PURPLE}Обучение прошло успешно!{Color.END}")
                            print(f"{Color.GREEN}Вы стали более харизматичным!{Color.END}")
                        
                        elif special_choice == '3':
                            print(f"\n{Color.PURPLE}Массаж от двух девушек...{Color.END}")
                            self.player.heal(80)
                            self.player.stamina = min(100, self.player.stamina + 50)
                            print(f"{Color.GREEN}+80 здоровья, +50 выносливости{Color.END}")
                    else:
                        print(f"{Color.RED}У вас недостаточно золота{Color.END}")
                
                time.sleep(2)
            
            elif choice == 4:
                if self.player.gold >= 100:
                    confirm = input("Отдохнуть в VIP-комнате за 100 золота? (y/n): ")
                    if confirm.lower() == 'y':
                        self.player.gold -= 100
                        print(f"\n{Color.PURPLE}VIP-комната...{Color.END}")
                        self.player.health = self.player.max_health
                        self.player.mana = self.player.max_mana
                        self.player.morale = 100
                        self.player.stamina = 100
                        
                        for girl in self.bordello_girls:
                            girl.rest()
                        
                        print(f"{Color.GREEN}Вы полностью отдохнули!{Color.END}")
                        print(f"{Color.CYAN}Все девушки восстановили силы.{Color.END}")
                else:
                    print(f"{Color.RED}У вас недостаточно золота{Color.END}")
                
                time.sleep(2)
            
            elif choice == 5:
                for girl in self.bordello_girls:
                    if random.random() < 0.3:
                        girl.rest()
                break
    
    def travel(self):
        """Путешествие между локациями"""
        while True:
            self.clear_screen()
            self.print_header("ПУТЕШЕСТВИЕ")
            
            current_loc = self.game_world.get(self.player.location)
            if not current_loc:
                print(f"{Color.RED}Ошибка: локация не найдена{Color.END}")
                return
            
            print(f"Текущая локация: {Color.YELLOW}{self.player.location}{Color.END}")
            print(f"Тип: {current_loc.type.value}")
            print(f"Уровень сложности: {current_loc.level_range[0]}-{current_loc.level_range[1]}")
            
            if current_loc.cleared:
                print(f"{Color.GREEN}✓ Локация очищена{Color.END}")
            
            print(f"\n{Color.CYAN}Доступные направления:{Color.END}")
            
            available_locations = []
            for i, loc_name in enumerate(current_loc.connections, 1):
                location = self.game_world.get(loc_name)
                if location:
                    status = "✓" if location.discovered else "?"
                    
                    if self.player.level < location.level_range[0]:
                        difficulty_warning = f" {Color.RED}(сложно){Color.END}"
                    elif self.player.level < location.level_range[0] + 2:
                        difficulty_warning = f" {Color.YELLOW}(нормально){Color.END}"
                    else:
                        difficulty_warning = f" {Color.GREEN}(легко){Color.END}"
                    
                    print(f"{i}. {loc_name} {status}{difficulty_warning}")
                    available_locations.append(loc_name)
            
            print(f"\n{len(available_locations) + 1}. Отмена")
            
            choice = self.get_choice(1, len(available_locations) + 1)
            
            if choice <= len(available_locations):
                target_loc_name = available_locations[choice - 1]
                target_loc = self.game_world[target_loc_name]
                
                difficulty_mult = {
                    Difficulty.EASY: 0.8,
                    Difficulty.NORMAL: 1.0,
                    Difficulty.HARD: 1.2,
                    Difficulty.INSANE: 1.5
                }.get(self.player.difficulty, 1.0)
                
                required_level = int(target_loc.level_range[0] * difficulty_mult)
                
                if self.player.level < required_level:
                    print(f"\n{Color.RED}Ваш уровень слишком низок для этой локации!{Color.END}")
                    print(f"Ваш уровень: {self.player.level}")
                    print(f"Требуется уровень: {required_level}")
                    print(f"Рекомендуется сначала повысить уровень.")
                    
                    confirm = input("Всё равно отправиться? (y/n): ")
                    if confirm.lower() != 'y':
                        continue
                
                print(f"\n{Color.YELLOW}Вы отправляетесь в {target_loc_name}...{Color.END}")
                time.sleep(1)
                
                events = [
                    ("Вы безопасно добрались до места", 0.5),
                    ("В пути вы нашли немного золота", 0.15),
                    ("На вас напали разбойники!", 0.1),
                    ("Вы заблудились и вернулись назад", 0.05),
                    ("Вы нашли короткий путь", 0.05),
                    ("Вы встретили странного торговца", 0.05),
                    ("Вы наткнулись на лагерь искателей приключений", 0.05),
                    ("Вы обнаружили тайник с припасами", 0.05)
                ]
                
                event = random.choices(
                    [e[0] for e in events],
                    weights=[e[1] for e in events]
                )[0]
                
                print(f"{Color.CYAN}{event}{Color.END}")
                
                if "золота" in event:
                    gold = random.randint(10, 50) + (self.player.level * 2)
                    self.player.gold += gold
                    print(f"{Color.YELLOW}+{gold} золота{Color.END}")
                
                elif "разбойники" in event:
                    time.sleep(1)
                    bandit_level = min(self.player.level + 1, target_loc.level_range[1])
                    bandit = Enemy(EnemyType.BANDIT, bandit_level, self.player.difficulty)
                    print(f"\n{Color.RED}На вас напали разбойники уровня {bandit_level}!{Color.END}")
                    self.battle(bandit, target_loc)
                    if self.player.health <= 0:
                        return
                
                elif "вернулись" in event:
                    print(f"{Color.YELLOW}Вы возвращаетесь в {self.player.location}.{Color.END}")
                    time.sleep(1)
                    continue
                
                elif "торговца" in event:
                    print(f"{Color.GREEN}Странный торговец предлагает вам товары по низким ценам!{Color.END}")
                
                elif "лагерь" in event:
                    print(f"{Color.CYAN}Искатели приключений делятся с вами припасами.{Color.END}")
                    self.player.heal(30)
                    print(f"{Color.GREEN}+30 здоровья{Color.END}")
                
                elif "тайник" in event:
                    print(f"{Color.GREEN}Вы нашли тайник с припасами!{Color.END}")
                    potions = ["Зелье здоровья", "Зелье маны"]
                    for potion_name in random.sample(potions, random.randint(1, 2)):
                        if potion_name in self.items_db:
                            potion = self.items_db[potion_name].copy()
                            self.player.add_item(potion)
                            print(f"{Color.CYAN}+ {potion.name}{Color.END}")
                
                self.player.location = target_loc_name
                target_loc.discovered = True
                
                if target_loc.should_respawn():
                    print(f"{Color.YELLOW}В локации появились новые враги.{Color.END}")
                
                print(f"\n{Color.GREEN}Вы прибыли в {target_loc_name}!{Color.END}")
                time.sleep(1)
                break
            
            else:
                break
    
    # ОПТИМИЗАЦИЯ: методы сохранения/загрузки
    def save_game(self):
        """Сохранение игры"""
        if not self.player:
            print(f"{Color.RED}Нет активного персонажа для сохранения{Color.END}")
            time.sleep(1)
            return
        
        save_data = {
            "version": self.version,
            "difficulty": self.player.difficulty.value,
            "player": {
                "name": self.player.name,
                "level": self.player.level,
                "xp": self.player.xp,
                "xp_to_next_level": self.player.xp_to_next_level,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "mana": self.player.mana,
                "max_mana": self.player.max_mana,
                "gold": self.player.gold,
                "character_class": self.player.character_class.value if self.player.character_class else None,
                "stats": self.player.stats,
                "location": self.player.location,
                "killed_enemies": self.player.killed_enemies,
                "play_time": self.player.play_time + (datetime.now() - self.game_start_time).seconds if self.game_start_time else 0,
                "save_slot": self.player.save_slot,
                "morale": self.player.morale,
                "stamina": self.player.stamina
            },
            "inventory": [
                {
                    "name": item.name,
                    "item_type": item.item_type.value,
                    "value": item.value,
                    "damage": item.damage,
                    "defense": item.defense,
                    "health": item.health,
                    "mana": item.mana,
                    "description": item.description,
                    "rarity": item.rarity,
                    "durability": item.durability,
                    "max_durability": item.max_durability,
                    "required_level": item.required_level,
                    "armor_slot": item.armor_slot,
                    "special_effect": item.special_effect
                }
                for item in self.player.inventory
            ],
            "equipped": {
                slot: {
                    "name": item.name,
                    "item_type": item.item_type.value,
                    "durability": item.durability,
                    "max_durability": item.max_durability,
                    "special_effect": item.special_effect
                } if item else None
                for slot, item in self.player.equipped.items()
            },
            "quests": [
                {
                    "id": quest.id,
                    "status": quest.status.value,
                    "start_time": quest.start_time.isoformat() if quest.start_time else None,
                    "completed_objectives": quest.completed_objectives,
                    "objectives": quest.objectives
                }
                for quest in self.player.quests
            ],
            "achievements": [
                {
                    "name": achievement.name,
                    "description": achievement.description,
                    "condition": achievement.condition,
                    "target_value": achievement.target_value,
                    "current_value": achievement.current_value,
                    "completed": achievement.completed,
                    "completion_date": achievement.completion_date.isoformat() if achievement.completion_date else None
                }
                for achievement in self.player.achievements
            ],
            "game_world": {
                loc_name: {
                    "discovered": loc.discovered,
                    "cleared": loc.cleared,
                    "respawn_timer": loc.respawn_timer
                }
                for loc_name, loc in self.game_world.items()
            }
        }
        
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)
        
        save_file = os.path.join(save_dir, f"save_{self.player.save_slot}.json")
        
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"{Color.GREEN}Игра успешно сохранена в слот {self.player.save_slot}!{Color.END}")
            
            if self.game_start_time:
                self.player.play_time += (datetime.now() - self.game_start_time).seconds
                self.game_start_time = datetime.now()
                
        except Exception as e:
            print(f"{Color.RED}Ошибка при сохранении: {e}{Color.END}")
        
        time.sleep(1)
    
    def save_game_menu(self):
        """Меню выбора слота для сохранения"""
        self.clear_screen()
        self.print_header("СОХРАНЕНИЕ ИГРЫ")
        
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"{Color.YELLOW}Выберите слот для сохранения:{Color.END}\n")
        
        for slot in range(1, 6):
            save_file = os.path.join(save_dir, f"save_{slot}.json")
            
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    player_data = save_data.get("player", {})
                    play_time = player_data.get("play_time", 0)
                    hours = play_time // 3600
                    minutes = (play_time % 3600) // 60
                    
                    print(f"{slot}. Слот {slot}: {player_data.get('name', 'Неизвестно')} "
                          f"(Ур.{player_data.get('level', 1)}, "
                          f"{player_data.get('character_class', 'Нет класса')})")
                    print(f"   Локация: {player_data.get('location', 'Неизвестно')}, "
                          f"Время: {hours}ч {minutes}м")
                    
                    if self.player and self.player.save_slot == slot:
                        print(f"   {Color.GREEN}← Текущая игра{Color.END}")
                except:
                    print(f"{slot}. Слот {slot}: {Color.RED}Ошибка загрузки{Color.END}")
            else:
                print(f"{slot}. Слот {slot}: {Color.YELLOW}Пусто{Color.END}")
        
        print(f"\n6. Быстрое сохранение (автоматически в текущий слот)")
        print(f"7. Отмена")
        
        choice = self.get_choice(1, 7)
        
        if choice in [1, 2, 3, 4, 5]:
            confirm = input(f"\nСохранить игру в слот {choice}? (y/n): ")
            if confirm.lower() == 'y':
                self.player.save_slot = choice
                self.save_game()
        elif choice == 6:
            self.save_game()
    
    def load_game_menu(self):
        """Меню выбора слота для загрузки"""
        self.clear_screen()
        self.print_header("ЗАГРУЗКА СОХРАНЕНИЯ")
        
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)
        
        saves = []
        print(f"{Color.YELLOW}Выберите сохранение для загрузки:{Color.END}\n")
        
        for slot in range(1, 6):
            save_file = os.path.join(save_dir, f"save_{slot}.json")
            
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    player_data = save_data.get("player", {})
                    play_time = player_data.get("play_time", 0)
                    hours = play_time // 3600
                    minutes = (play_time % 3600) // 60
                    
                    version = save_data.get("version", "1.0.0")
                    version_text = f" [v{version}]" if version != self.version else ""
                    
                    print(f"{slot}. {player_data.get('name', 'Неизвестно')} "
                          f"(Ур.{player_data.get('level', 1)}, "
                          f"{player_data.get('character_class', 'Нет класса')}){version_text}")
                    print(f"   Локация: {player_data.get('location', 'Неизвестно')}, "
                          f"Время: {hours}ч {minutes}м")
                    
                    saves.append(slot)
                except Exception as e:
                    print(f"{slot}. Слот {slot}: {Color.RED}Ошибка загрузки{Color.END}")
                    print(f"   {str(e)[:50]}...")
            else:
                print(f"{slot}. Слот {slot}: {Color.YELLOW}Пусто{Color.END}")
        
        if not saves:
            print(f"\n{Color.YELLOW}Нет доступных сохранений{Color.END}")
            print("Создайте нового персонажа, чтобы начать игру.")
            time.sleep(2)
            return
        
        print(f"\n{len(saves) + 1}. Отмена")
        
        choice = self.get_choice(1, len(saves) + 1)
        
        if choice <= len(saves):
            save_slot = saves[choice - 1]
            self.load_save_file(save_slot)
    
    def load_save_file(self, slot: int):
        """Загрузка конкретного файла сохранения"""
        save_file = os.path.join("saves", f"save_{slot}.json")
        
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            save_version = save_data.get("version", "1.0.0")
            if save_version != self.version:
                print(f"{Color.YELLOW}Внимание: сохранение создано в версии {save_version}, текущая версия {self.version}{Color.END}")
                print("Возможны проблемы с совместимостью.")
                confirm = input("Продолжить загрузку? (y/n): ")
                if confirm.lower() != 'y':
                    return
            
            difficulty_str = save_data.get("difficulty", "Нормальный")
            difficulty_map = {
                "Легкий": Difficulty.EASY,
                "Нормальный": Difficulty.NORMAL,
                "Сложный": Difficulty.HARD,
                "Безумный": Difficulty.INSANE
            }
            self.difficulty = difficulty_map.get(difficulty_str, Difficulty.NORMAL)
            
            player_data = save_data["player"]
            self.player = Player(player_data["name"], self.difficulty)
            self.player.level = player_data["level"]
            self.player.xp = player_data["xp"]
            self.player.xp_to_next_level = player_data["xp_to_next_level"]
            self.player.health = player_data["health"]
            self.player.max_health = player_data["max_health"]
            self.player.mana = player_data["mana"]
            self.player.max_mana = player_data["max_mana"]
            self.player.gold = player_data["gold"]
            
            class_map = {
                "Воин": CharacterClass.WARRIOR,
                "Маг": CharacterClass.MAGE,
                "Лучник": CharacterClass.ARCHER,
                "Разбойник": CharacterClass.ROGUE
            }
            self.player.character_class = class_map.get(player_data["character_class"])
            
            self.player.stats = player_data["stats"]
            self.player.location = player_data["location"]
            self.player.killed_enemies = player_data.get("killed_enemies", {})
            self.player.save_slot = player_data.get("save_slot", slot)
            self.player.play_time = player_data.get("play_time", 0)
            self.player.morale = player_data.get("morale", 100)
            self.player.stamina = player_data.get("stamina", 100)
            
            for item_data in save_data["inventory"]:
                try:
                    item_type = ItemType(item_data["item_type"])
                    item = Item(
                        name=item_data["name"],
                        item_type=item_type,
                        value=item_data["value"],
                        damage=item_data.get("damage", 0),
                        defense=item_data.get("defense", 0),
                        health=item_data.get("health", 0),
                        mana=item_data.get("mana", 0),
                        description=item_data["description"],
                        durability=item_data.get("durability", 100),
                        required_level=item_data.get("required_level", 1),
                        armor_slot=item_data.get("armor_slot"),
                        special_effect=item_data.get("special_effect")
                    )
                    item.rarity = item_data.get("rarity", "Обычный")
                    self.player.add_item(item)
                except Exception as e:
                    print(f"{Color.YELLOW}Предупреждение: не удалось загрузить предмет {item_data.get('name', 'Неизвестно')}: {e}{Color.END}")
            
            equipped_data = save_data.get("equipped", {})
            for slot_name, item_data in equipped_data.items():
                if item_data:
                    for item in self.player.inventory:
                        if item.name == item_data["name"]:
                            item.durability = item_data.get("durability", item.durability)
                            item.max_durability = item_data.get("max_durability", item.max_durability)
                            if "special_effect" in item_data:
                                item.special_effect = item_data["special_effect"]
                            
                            self.player.equipped[slot_name] = item
                            self.player.inventory.remove(item)
                            break
            
            self.player.quests = []
            for quest_data in save_data.get("quests", []):
                quest_id = quest_data.get("id")
                if quest_id in self.quests_db:
                    quest = copy.deepcopy(self.quests_db[quest_id])
                    quest.status = QuestStatus(quest_data.get("status", "NOT_STARTED"))
                    
                    start_time_str = quest_data.get("start_time")
                    if start_time_str:
                        quest.start_time = datetime.fromisoformat(start_time_str)
                    
                    quest.completed_objectives = quest_data.get("completed_objectives", {})
                    quest.objectives = quest_data.get("objectives", {})
                    self.player.quests.append(quest)
            
            self.player.achievements = []
            for achievement_data in save_data.get("achievements", []):
                achievement = Achievement(
                    name=achievement_data["name"],
                    description=achievement_data["description"],
                    condition=achievement_data["condition"],
                    target_value=achievement_data["target_value"],
                    reward_xp=achievement_data.get("reward_xp", 0),
                    reward_gold=achievement_data.get("reward_gold", 0)
                )
                achievement.current_value = achievement_data.get("current_value", 0)
                achievement.completed = achievement_data.get("completed", False)
                
                completion_date_str = achievement_data.get("completion_date")
                if completion_date_str:
                    achievement.completion_date = datetime.fromisoformat(completion_date_str)
                
                self.player.achievements.append(achievement)
            
            for loc_name, loc_data in save_data.get("game_world", {}).items():
                if loc_name in self.game_world:
                    self.game_world[loc_name].discovered = loc_data.get("discovered", False)
                    self.game_world[loc_name].cleared = loc_data.get("cleared", False)
                    self.game_world[loc_name].respawn_timer = loc_data.get("respawn_timer", 0)
            
            self.game_start_time = datetime.now()
            
            print(f"{Color.GREEN}Игра успешно загружена!{Color.END}")
            time.sleep(1)
            
        except Exception as e:
            print(f"{Color.RED}Ошибка при загрузке: {e}{Color.END}")
            import traceback
            traceback.print_exc()
            time.sleep(2)
    
    def view_saves(self):
        """Просмотр всех сохранений"""
        self.clear_screen()
        self.print_header("ПРОСМОТР СОХРАНЕНИЙ")
        
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"{Color.CYAN}Список сохранений:{Color.END}\n")
        
        for slot in range(1, 6):
            save_file = os.path.join(save_dir, f"save_{slot}.json")
            
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    player_data = save_data.get("player", {})
                    play_time = player_data.get("play_time", 0)
                    hours = play_time // 3600
                    minutes = (play_time % 3600) // 60
                    seconds = play_time % 60
                    
                    version = save_data.get("version", "1.0.0")
                    
                    print(f"{Color.GREEN}Слот {slot}:{Color.END}")
                    print(f"  Имя: {player_data.get('name', 'Неизвестно')}")
                    print(f"  Уровень: {player_data.get('level', 1)}")
                    print(f"  Класс: {player_data.get('character_class', 'Нет класса')}")
                    print(f"  Локация: {player_data.get('location', 'Неизвестно')}")
                    print(f"  Золото: {player_data.get('gold', 0)}")
                    print(f"  Время игры: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    print(f"  Версия: {version}")
                    
                    achievements = save_data.get("achievements", [])
                    completed = len([a for a in achievements if a.get("completed", False)])
                    total = len(achievements) if achievements else 0
                    if total > 0:
                        print(f"  Достижения: {completed}/{total}")
                    
                    if self.player and self.player.save_slot == slot:
                        print(f"  {Color.YELLOW}← Текущая активная игра{Color.END}")
                    
                except Exception as e:
                    print(f"{Color.RED}Слот {slot}: Ошибка загрузка{Color.END}")
                    print(f"  {str(e)[:50]}...")
            else:
                print(f"{Color.YELLOW}Слот {slot}: Пусто{Color.END}")
            
            print()
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы вернуться...{Color.END}")
    
    def delete_save_menu(self):
        """Меню удаления сохранения"""
        self.clear_screen()
        self.print_header("УДАЛЕНИЕ СОХРАНЕНИЙ")
        
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)
        
        saves = []
        print(f"{Color.RED}Выберите сохранение для удаления:{Color.END}\n")
        
        for slot in range(1, 6):
            save_file = os.path.join(save_dir, f"save_{slot}.json")
            
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    player_data = save_data.get("player", {})
                    play_time = player_data.get("play_time", 0)
                    hours = play_time // 3600
                    minutes = (play_time % 3600) // 60
                    
                    print(f"{slot}. {player_data.get('name', 'Неизвестно')} "
                          f"(Ур.{player_data.get('level', 1)})")
                    print(f"   Класс: {player_data.get('character_class', 'Нет класса')}")
                    print(f"   Время игры: {hours}ч {minutes}м")
                    
                    saves.append(slot)
                except:
                    print(f"{slot}. Слот {slot}: {Color.RED}Ошибка{Color.END}")
            else:
                print(f"{slot}. Слот {slot}: {Color.YELLOW}Пусто{Color.END}")
        
        if not saves:
            print(f"\n{Color.YELLOW}Нет сохранений для удаления{Color.END}")
            time.sleep(2)
            return
        
        print(f"\n{len(saves) + 1}. Удалить ВСЕ сохранения")
        print(f"{len(saves) + 2}. Отмена")
        
        choice = self.get_choice(1, len(saves) + 2)
        
        if choice <= len(saves):
            save_slot = saves[choice - 1]
            confirm = input(f"\n{Color.RED}ВНИМАНИЕ! Вы уверены, что хотите удалить сохранение в слоте {save_slot}? (y/n): {Color.END}")
            
            if confirm.lower() == 'y':
                save_file = os.path.join(save_dir, f"save_{save_slot}.json")
                try:
                    os.remove(save_file)
                    print(f"{Color.GREEN}Сохранение удалено!{Color.END}")
                    
                    if self.player and self.player.save_slot == save_slot:
                        print(f"{Color.YELLOW}Текущая игра завершена.{Color.END}")
                        self.player = None
                except Exception as e:
                    print(f"{Color.RED}Ошибка при удалении: {e}{Color.END}")
                
                time.sleep(2)
        
        elif choice == len(saves) + 1:
            confirm = input(f"\n{Color.RED}ВНИМАНИЕ! Вы уверены, что хотите удалить ВСЕ сохранения? (y/n): {Color.END}")
            
            if confirm.lower() == 'y':
                deleted = 0
                for slot in range(1, 6):
                    save_file = os.path.join(save_dir, f"save_{slot}.json")
                    if os.path.exists(save_file):
                        try:
                            os.remove(save_file)
                            deleted += 1
                        except:
                            pass
                
                print(f"{Color.GREEN}Удалено {deleted} сохранений!{Color.END}")
                
                if self.player:
                    print(f"{Color.YELLOW}Текущая игра завершена.{Color.END}")
                    self.player = None
                
                time.sleep(2)
    
    def manage_saves_menu(self):
        """Меню управления сохранениями"""
        while True:
            self.clear_screen()
            self.print_header("УПРАВЛЕНИЕ СОХРАНЕНИЯМИ")
        
            print(f"{Color.YELLOW}Выберите действие:{Color.END}\n")
            print("1. Просмотр сохранений")
            print("2. Удалить сохранение")
            print("3. Копировать сохранение")
            print("4. Назад в главное меню")
        
            choice = self.get_choice(1, 4)
        
            if choice == 1:
                self.view_saves()
            elif choice == 2:
                self.delete_save_menu()
            elif choice == 3:
                self.copy_save_menu()
            elif choice == 4:
                break
    
    def copy_save_menu(self):
        """Копирование сохранения"""
        self.clear_screen()
        self.print_header("КОПИРОВАНИЕ СОХРАНЕНИЯ")
        
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)
        
        saves = []
        for slot in range(1, 6):
            save_file = os.path.join(save_dir, f"save_{slot}.json")
            if os.path.exists(save_file):
                saves.append(slot)
        
        if not saves:
            print(f"{Color.YELLOW}Нет сохранений для копирования{Color.END}")
            time.sleep(2)
            return
        
        print(f"{Color.YELLOW}Выберите сохранение для копирования:{Color.END}\n")
        
        for slot in saves:
            print(f"{slot}. Слот {slot}")
        
        print(f"\n{len(saves) + 1}. Отмена")
        
        source_choice = self.get_choice(1, len(saves) + 1)
        
        if source_choice <= len(saves):
            source_slot = saves[source_choice - 1]
            
            print(f"\n{Color.YELLOW}Выберите слот для копирования:{Color.END}\n")
            
            target_slots = []
            for slot in range(1, 6):
                if slot != source_slot:
                    target_slots.append(slot)
                    print(f"{len(target_slots)}. Слот {slot}")
            
            print(f"\n{len(target_slots) + 1}. Отмена")
            
            target_choice = self.get_choice(1, len(target_slots) + 1)
            
            if target_choice <= len(target_slots):
                target_slot = target_slots[target_choice - 1]
                
                confirm = input(f"\nСкопировать сохранение из слота {source_slot} в слот {target_slot}? (y/n): ")
                if confirm.lower() == 'y':
                    source_file = os.path.join(save_dir, f"save_{source_slot}.json")
                    target_file = os.path.join(save_dir, f"save_{target_slot}.json")
                    
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                        
                        if "player" in save_data:
                            save_data["player"]["save_slot"] = target_slot
                        
                        with open(target_file, 'w', encoding='utf-8') as f:
                            json.dump(save_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"{Color.GREEN}Сохранение успешно скопировано!{Color.END}")
                    except Exception as e:
                        print(f"{Color.RED}Ошибка при копировании: {e}{Color.END}")
                    
                    time.sleep(2)
    
    def show_achievements(self):
        """Показать достижения"""
        self.clear_screen()
        self.print_header("ДОСТИЖЕНИЯ")
        
        if not self.player.achievements:
            print(f"{Color.YELLOW}Достижения не загружены{Color.END}")
        else:
            completed = [a for a in self.player.achievements if a.completed]
            in_progress = [a for a in self.player.achievements if not a.completed]
            
            print(f"{Color.GREEN}Завершено: {len(completed)}/{len(self.player.achievements)}{Color.END}")
            
            if completed:
                print(f"\n{Color.BOLD}ЗАВЕРШЕННЫЕ:{Color.END}")
                for achievement in completed:
                    completion_date = achievement.completion_date.strftime("%d.%m.%Y %H:%M") if achievement.completion_date else "Неизвестно"
                    print(f"  ✓ {achievement.name}")
                    print(f"     {achievement.description}")
                    print(f"     Награда: {achievement.reward_xp} опыта, {achievement.reward_gold} золота")
                    print(f"     Получено: {completion_date}")
                    print()
            
            if in_progress:
                print(f"\n{Color.BOLD}В ПРОЦЕССЕ:{Color.END}")
                for achievement in in_progress:
                    progress = f"{achievement.current_value}/{achievement.target_value}"
                    print(f"  ○ {achievement.name} [{progress}]")
                    print(f"     {achievement.description}")
                    print()
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы вернуться...{Color.END}")
    
    def show_about(self):
        """Информация об игре"""
        self.clear_screen()
        self.print_header("ОБ ИГРЕ")
        
        print(f"{Color.CYAN}ДРАКОНОВОЕ ЗАКЛИНАНИЕ - УЛУЧШЕННАЯ ВЕРСИЯ 2.0.3{Color.END}")
        print("Полноценная текстовая RPG игра")
        print(f"Версия: {self.version}")
        print("\nИсправления и улучшения версии 2.0.3:")
        print("• Исправлено количество врагов на локациях (теперь 5-10 вместо 2-8)")
        print("• Добавлены специальные эффекты для всего оружия")
        print("• Оптимизирован код без потери функциональности")
        print("• Исправлены мелкие баги и улучшена стабильность")
        
        print(f"\n{Color.BOLD}СПЕЦИАЛЬНЫЕ ЭФФЕКТЫ ОРУЖИЯ:{Color.END}")
        print("• Огненный урон - дополнительный урон огнем")
        print("• Кража маны - восстанавливает ману при ударе")
        print("• Шанс крита - увеличивает шанс критического удара")
        print("• Яд - наносит дополнительный урон ядом")
        print("• Кража здоровья - восстанавливает здоровье при ударе")
        print("• Оглушение - шанс оглушить врага на 1 ход")
        print("• Пробитие брони - игнорирует часть защиты врага")
        
        print(f"\n{Color.BOLD}ИСПРАВЛЕНИЯ:{Color.END}")
        print("• Увеличены враги на локациях с 2-8 до 5-10")
        print("• Добавлены новые виды оружия для всех классов")
        print("• Улучшена система специальных эффектов")
        print("• Оптимизированы методы вывода информации")
        
        print(f"\n{Color.YELLOW}Удачи в приключениях!{Color.END}")
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы вернуться...{Color.END}")
    
    def show_help(self):
        """Показать справку по игре"""
        self.clear_screen()
        self.print_header("СПРАВКА ПО ИГРЕ")
        
        print(f"{Color.YELLOW}ОСНОВНЫЕ КОМАНДЫ:{Color.END}")
        print("• Во время выбора опций вводите цифру соответствующего пункта")
        print("• Для выхода из игры введите 'выход', 'exit' или 'quit'")
        print("• В бою внимательно читайте опции действий")
        
        print(f"\n{Color.YELLOW}НОВЫЕ ФУНКЦИИ 2.0.3:{Color.END}")
        print("• Оружие теперь имеет специальные эффекты:")
        print("  - Огненный/ледяной урон - дополнительный урон")
        print("  - Кража маны/здоровья - восстановление при ударе")
        print("  - Яд - дополнительный урон в течение нескольких ходов")
        print("  - Оглушение - шанс пропуска хода врага")
        print("  - Пробитие брони - игнорирует защиту врага")
        
        print(f"\n{Color.YELLOW}ХАРАКТЕРИСТИКИ ПЕРСОНАЖА:{Color.END}")
        print("• Сила - увеличивает урон в ближнем бою")
        print("• Ловкость - увеличивает шанс крита и уклонения")
        print("• Интеллект - увеличивает ману и эффективность магии")
        print("• Телосложение - увеличивает здоровье и защиту")
        print("• Удача - увеличивает шанс на редкий лут и крит")
        
        print(f"\n{Color.YELLOW}СИСТЕМА БОЯ:{Color.END}")
        print("• Каждый ход вы можете атаковать, использовать предмет или умение")
        print("• У каждого класса есть уникальные умения")
        print("• Некоторые враги имеют особые способности")
        print("• Вы можете попытаться сбежать из боя")
        
        print(f"\n{Color.YELLOW}ЭКИПИРОВКА И ПРЕДМЕТЫ:{Color.END}")
        print("• Оружие и броня имеют прочность, которая уменьшается в бою")
        print("• Ремонтировать экипировку можно в магазинах")
        print("• Зелья можно использовать для восстановления здоровья/маны")
        print("• Свитки имеют различные магические эффекты")
        
        print(f"\n{Color.YELLOW}КВЕСТЫ И ЗАДАНИЯ:{Color.END}")
        print("• Основные квесты продвигают сюжет")
        print("• Побочные квесты дают дополнительный опыт и золото")
        print("• Некоторые квесты имеют временные ограничения")
        print("• Получайте квесты в тавернах и от NPC")
        
        print(f"\n{Color.YELLOW}СОВЕТЫ ДЛЯ НОВИЧКОВ:{Color.END}")
        print("1. Начинайте с легкой сложности")
        print("2. Прокачивайте характеристики равномерно")
        print("3. Не забывайте ремонтировать экипировку")
        print("4. Выполняйте побочные квесты для прокачки")
        print("5. Сохраняйтесь перед сложными битвами")
        print("6. Обращайте внимание на специальные эффекты оружия")
        
        input(f"\n{Color.WHITE}Нажмите Enter, чтобы вернуться...{Color.END}")
    
    def main_menu(self):
        """Главное меню"""
        while self.is_running:
            self.clear_screen()
            self.print_header("ДРАКОНОВОЕ ЗАКЛИНАНИЕ - УЛУЧШЕННАЯ ВЕРСИЯ")
            
            print(f"{Color.CYAN}Добро пожаловать в эпическую RPG игру!{Color.END}")
            print(f"{Color.YELLOW}Версия: {self.version}{Color.END}")
            
            if self.player:
                print(f"\n{Color.GREEN}Текущий персонаж:{Color.END}")
                print(f"Имя: {self.player.name}")
                print(f"Класс: {self.player.character_class.value}")
                print(f"Уровень: {self.player.level}")
                print(f"Локация: {self.player.location}")
            
            print(f"\n{Color.YELLOW}ВЫБЕРИТЕ ДЕЙСТВИЕ:{Color.END}")
            
            menu_options = []
            if self.player:
                menu_options = [
                    ("1", "Новая игра"),
                    ("2", "Загрузить игру"),
                    ("3", "Продолжить"),
                    ("4", "Управление сохранениями"),
                    ("5", "Достижения"),
                    ("6", "Об игре"),
                    ("7", "Справка"),
                    ("8", "Выйти")
                ]
            else:
                menu_options = [
                    ("1", "Новая игра"),
                    ("2", "Загрузить игру"),
                    ("3", "Управление сохранениями"),
                    ("4", "Об игре"),
                    ("5", "Справка"),
                    ("6", "Выйти")
                ]
            
            for key, desc in menu_options:
                print(f"{Color.GREEN}{key}. {desc}{Color.END}")
            
            print(f"{Color.CYAN}{'-'*70}{Color.END}")
            
            max_choice = len(menu_options)
            choice = self.get_choice(1, max_choice)
            
            if self.player:
                if choice == 1:
                    confirm = input("Начать новую игру? Текущий прогресс будет потерян. (y/n): ")
                    if confirm.lower() == 'y':
                        self.create_character()
                        self.game_start_time = datetime.now()
                        self.game_loop()
                
                elif choice == 2:
                    self.load_game_menu()
                    if self.player:
                        self.game_start_time = datetime.now()
                        self.game_loop()
                
                elif choice == 3:
                    self.game_loop()
                
                elif choice == 4:
                    self.manage_saves_menu()
                
                elif choice == 5:
                    self.show_achievements()
                
                elif choice == 6:
                    self.show_about()
                
                elif choice == 7:
                    self.show_help()
                
                elif choice == 8:
                    print(f"\n{Color.YELLOW}До свидания!{Color.END}")
                    self.is_running = False
            
            else:
                if choice == 1:
                    self.create_character()
                    self.game_start_time = datetime.now()
                    self.game_loop()
                
                elif choice == 2:
                    self.load_game_menu()
                    if self.player:
                        self.game_start_time = datetime.now()
                        self.game_loop()
                
                elif choice == 3:
                    self.manage_saves_menu()
                
                elif choice == 4:
                    self.show_about()
                
                elif choice == 5:
                    self.show_help()
                
                elif choice == 6:
                    print(f"\n{Color.YELLOW}До свидания!{Color.END}")
                    self.is_running = False
    
    def game_loop(self):
        """Основной игровой цикл"""
        while self.is_running and self.player and self.player.health > 0:
            self.clear_screen()
            
            current_loc = self.game_world.get(self.player.location)
            if not current_loc:
                print(f"{Color.RED}Ошибка: локация не найдена{Color.END}")
                break
            
            self.print_header(f"{self.player.location.upper()}")
            
            print(f"{Color.CYAN}{current_loc.description}{Color.END}")
            print(f"Тип: {current_loc.type.value}")
            print(f"Уровень сложности: {current_loc.level_range[0]}-{current_loc.level_range[1]}")
            
            print(f"\n{Color.GREEN}{self.player.name} (Ур.{self.player.level}){Color.END}")
            health_bar = self.create_bar(self.player.health, self.player.max_health, 20)
            mana_bar = self.create_bar(self.player.mana, self.player.max_mana, 20, Color.BLUE, Color.BLUE, Color.PURPLE)
            print(f"Здоровье: {health_bar}")
            print(f"Мана:     {mana_bar}")
            print(f"Золото: {Color.YELLOW}{self.player.gold}{Color.END}")
            
            if current_loc.cleared:
                print(f"{Color.GREEN}✓ Локация очищена{Color.END}")
            elif current_loc.enemies:
                print(f"{Color.RED}⚠ Враги присутствуют ({len(current_loc.enemies)}){Color.END}")
            else:
                print(f"{Color.YELLOW}○ Врагов нет{Color.END}")
            
            print(f"\n{Color.CYAN}{'-'*70}{Color.END}")
            
            menu_options = []
            
            menu_options.append(("1", "Исследовать локацию"))
            menu_options.append(("2", "Путешествовать"))
            
            if current_loc.type == LocationType.TOWN:
                if current_loc.has_tavern:
                    menu_options.append(("3", "Посетить таверну"))
                if current_loc.has_shop:
                    menu_options.append(("4", "Посетить магазин"))
                if current_loc.has_bordello:
                    menu_options.append(("5", "Посетить бордель"))
                menu_options.append(("6", "Поговорить с жителями"))
            
            menu_options.append(("7", "Статус персонажа"))
            menu_options.append(("8", "Инвентарь"))
            menu_options.append(("9", "Квесты"))
            menu_options.append(("10", "Достижения"))
            menu_options.append(("11", "Сохранить игру"))
            menu_options.append(("12", "Выйти в главное меню"))
            
            renumbered_options = []
            for i, (_, desc) in enumerate(menu_options, 1):
                renumbered_options.append((str(i), desc))
            
            for key, desc in renumbered_options:
                print(f"{key}. {desc}")
            
            choice = self.get_choice(1, len(menu_options))
            
            if choice == 1:
                self.explore_location(current_loc)
            elif choice == 2:
                self.travel()
            elif choice == 3 and current_loc.type == LocationType.TOWN and current_loc.has_tavern:
                self.visit_tavern()
            elif choice == 4 and current_loc.type == LocationType.TOWN and current_loc.has_shop:
                self.visit_shop()
            elif choice == 5 and current_loc.type == LocationType.TOWN and current_loc.has_bordello:
                self.visit_bordello()
            elif choice == 6 and current_loc.type == LocationType.TOWN:
                self.talk_to_npcs()
            elif choice == 7:
                self.show_status()
            elif choice == 8:
                self.show_inventory()
            elif choice == 9:
                self.show_quests()
            elif choice == 10:
                self.show_achievements()
            elif choice == 11:
                self.save_game_menu()
            elif choice == 12:
                break
            
            if self.player and self.player.health <= 0:
                return
        
        if self.player and self.player.health <= 0:
            self.game_over()
    
    def run(self):
        """Запуск игры"""
        try:
            print(f"{Color.CYAN}Загрузка игры 'Драконовое заклинание - Улучшенная версия 2.0.3'...{Color.END}")
            time.sleep(1)
            
            self.main_menu()
            
            print(f"\n{Color.YELLOW}Игра завершена. До свидания!{Color.END}")
        except Exception as e:
            print(f"\n{Color.RED}Критическая ошибка при запуске игры: {e}{Color.END}")
            import traceback
            traceback.print_exc()
            input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        print(f"{Color.CYAN}Загрузка игры 'Драконовое заклинание - Улучшенная версия 2.0.3'...{Color.END}")
        time.sleep(1)
        
        game = Game()
        game.run()
        
        print(f"\n{Color.YELLOW}Игра завершена. До свидания!{Color.END}")
    except Exception as e:
        print(f"\n{Color.RED}Критическая ошибка при запуске игры: {e}{Color.END}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
