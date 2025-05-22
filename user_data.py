import json
import os

class UserDataManager:
    def __init__(self, filepath='users.json'):
        self.filepath = filepath
        self.users = {}  # Armazena usuários como {username: {"password": senha, "age": idade, "acertos": 0, "erros": 0, "tempo": 0}}
        self.load_users()

    def load_users(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.users = {}
        else:
            self.users = {}

    def save_users(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erro ao salvar usuários: {e}")

    def add_user(self, username, password, age, callback=None):
        if username in self.users:
            raise ValueError("Usuário já existe.")
        if not isinstance(age, int) or age <= 0:
            raise ValueError("Idade deve ser um número inteiro positivo.")
        self.users[username] = {"password": password, "age": age, "acertos": 0, "erros": 0, "tempo": 0}
        self.save_users()
        if callback:
            callback(username, self.users[username])

    def validate_user(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            return True
        return False

    def record_quiz_result(self, username, acertos, erros, tempo):
        if username not in self.users:
            raise ValueError("Usuário não encontrado.")
        self.users[username]["acertos"] += acertos
        self.users[username]["erros"] += erros
        self.users[username]["tempo"] += tempo
        self.save_users()

    def get_user_data(self, username):
        return self.users.get(username, None)
