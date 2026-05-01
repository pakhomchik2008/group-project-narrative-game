import unittest


# ---------------------------------------------------------------------------
# Classes (fixed from "12 jan class.py" — original has indentation bugs and
# extra `self` passed to super().__init__() in Rogue and *Warrior subclasses)
# ---------------------------------------------------------------------------

class Characters:
    def __init__(self, strength, magic, dexterity, health_points):
        self.strength = strength
        self.magic = magic
        self.dexterity = dexterity
        self.health_points = health_points

    def show_strength(self):
        print('strength is', self.strength)

    def show_magic(self):
        print('magic is', self.magic)

    def show_dexterity(self):
        print('dexterity is', self.dexterity)

    def show_health_points(self):
        print('health_points is', self.health_points)


class Warrior(Characters):
    def __init__(self, strength, magic, dexterity, health_points, weapon):
        super().__init__(strength, magic, dexterity, health_points)
        self.weapon = weapon


class Mage(Characters):
    def __init__(self, strength, magic, dexterity, health_points, spell_power):
        super().__init__(strength, magic, dexterity, health_points)
        self.spell_power = spell_power


class Rogue(Characters):
    def __init__(self, strength, magic, dexterity, health_points, stealth):
        super().__init__(strength, magic, dexterity, health_points)  # removed extra self
        self.stealth = stealth


class NoviceWarrior(Warrior):
    def __init__(self, strength, magic, dexterity, health_points, weapon):
        super().__init__(strength, magic, dexterity, health_points, weapon)  # removed extra self
        self.level = 'novice'


class AdvancedWarrior(Warrior):
    def __init__(self, strength, magic, dexterity, health_points, weapon):
        super().__init__(strength, magic, dexterity, health_points, weapon)  # removed extra self
        self.level = 'advanced'


class IntermediateWarrior(Warrior):
    def __init__(self, strength, magic, dexterity, health_points, weapon):
        super().__init__(strength, magic, dexterity, health_points, weapon)  # removed extra self
        self.level = 'intermediate'


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCharacters(unittest.TestCase):

    def setUp(self):
        self.char = Characters(strength=10, magic=5, dexterity=8, health_points=100)

    def test_attributes_stored_correctly(self):
        self.assertEqual(self.char.strength, 10)
        self.assertEqual(self.char.magic, 5)
        self.assertEqual(self.char.dexterity, 8)
        self.assertEqual(self.char.health_points, 100)

    def test_is_instance_of_characters(self):
        self.assertIsInstance(self.char, Characters)


class TestWarrior(unittest.TestCase):

    def setUp(self):
        self.warrior = Warrior(strength=15, magic=2, dexterity=10, health_points=120, weapon='sword')

    def test_inherits_base_attributes(self):
        self.assertEqual(self.warrior.strength, 15)
        self.assertEqual(self.warrior.magic, 2)
        self.assertEqual(self.warrior.dexterity, 10)
        self.assertEqual(self.warrior.health_points, 120)

    def test_weapon_attribute(self):
        self.assertEqual(self.warrior.weapon, 'sword')

    def test_is_subclass_of_characters(self):
        self.assertIsInstance(self.warrior, Characters)


class TestMage(unittest.TestCase):

    def setUp(self):
        self.mage = Mage(strength=4, magic=20, dexterity=7, health_points=80, spell_power=50)

    def test_inherits_base_attributes(self):
        self.assertEqual(self.mage.strength, 4)
        self.assertEqual(self.mage.magic, 20)
        self.assertEqual(self.mage.health_points, 80)

    def test_spell_power_attribute(self):
        self.assertEqual(self.mage.spell_power, 50)

    def test_is_subclass_of_characters(self):
        self.assertIsInstance(self.mage, Characters)


class TestRogue(unittest.TestCase):

    def setUp(self):
        self.rogue = Rogue(strength=8, magic=6, dexterity=18, health_points=90, stealth=75)

    def test_inherits_base_attributes(self):
        self.assertEqual(self.rogue.dexterity, 18)
        self.assertEqual(self.rogue.health_points, 90)

    def test_stealth_attribute(self):
        self.assertEqual(self.rogue.stealth, 75)

    def test_is_subclass_of_characters(self):
        self.assertIsInstance(self.rogue, Characters)


class TestWarriorSubclasses(unittest.TestCase):

    def test_novice_warrior_level(self):
        nw = NoviceWarrior(10, 2, 8, 100, 'axe')
        self.assertEqual(nw.level, 'novice')
        self.assertEqual(nw.weapon, 'axe')
        self.assertIsInstance(nw, Warrior)
        self.assertIsInstance(nw, Characters)

    def test_advanced_warrior_level(self):
        aw = AdvancedWarrior(20, 3, 12, 150, 'greatsword')
        self.assertEqual(aw.level, 'advanced')
        self.assertEqual(aw.weapon, 'greatsword')

    def test_intermediate_warrior_level(self):
        iw = IntermediateWarrior(15, 2, 10, 130, 'spear')
        self.assertEqual(iw.level, 'intermediate')
        self.assertEqual(iw.weapon, 'spear')

    def test_all_three_are_warrior_subclasses(self):
        for cls, level in [(NoviceWarrior, 'novice'),
                           (AdvancedWarrior, 'advanced'),
                           (IntermediateWarrior, 'intermediate')]:
            with self.subTest(cls=cls.__name__):
                obj = cls(10, 2, 8, 100, 'dagger')
                self.assertIsInstance(obj, Warrior)
                self.assertEqual(obj.level, level)


if __name__ == '__main__':
    unittest.main()
