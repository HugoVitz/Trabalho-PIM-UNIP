import unittest
from user_data import UserDataManager

class TestUserDataManager(unittest.TestCase):
    def setUp(self):
        self.manager = UserDataManager()

    def test_add_user_success(self):
        self.manager.add_user("user1", "pass1", 25)
        self.assertIn("user1", self.manager.users)
        self.assertEqual(self.manager.users["user1"]["age"], 25)

    def test_add_user_duplicate(self):
        self.manager.add_user("user1", "pass1", 25)
        with self.assertRaises(ValueError):
            self.manager.add_user("user1", "pass2", 30)

    def test_add_user_invalid_age(self):
        with self.assertRaises(ValueError):
            self.manager.add_user("user2", "pass2", -5)
        with self.assertRaises(ValueError):
            self.manager.add_user("user3", "pass3", 0)
        with self.assertRaises(ValueError):
            self.manager.add_user("user4", "pass4", "abc")

    def test_validate_user(self):
        self.manager.add_user("user1", "pass1", 25)
        self.assertTrue(self.manager.validate_user("user1", "pass1"))
        self.assertFalse(self.manager.validate_user("user1", "wrongpass"))
        self.assertFalse(self.manager.validate_user("nonexistent", "pass"))

    def test_record_quiz_result(self):
        self.manager.add_user("user1", "pass1", 25)
        self.manager.record_quiz_result("user1", 3, 1, 120.5)
        user_data = self.manager.get_user_data("user1")
        self.assertEqual(user_data["acertos"], 3)
        self.assertEqual(user_data["erros"], 1)
        self.assertAlmostEqual(user_data["tempo"], 120.5)

    def test_record_quiz_result_invalid_user(self):
        with self.assertRaises(ValueError):
            self.manager.record_quiz_result("nonexistent", 1, 0, 30)

if __name__ == "__main__":
    unittest.main()
