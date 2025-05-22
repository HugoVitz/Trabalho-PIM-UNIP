import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import time

# --- user_data.py ---
class UserDataManager:
    def __init__(self, filename="users.json"):
        self.filename = filename
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=4)

    def add_user(self, username, password, age, callback=None):
        if username in self.users:
            raise ValueError("Nome de usuário já existe.")
        self.users[username] = {"password": password, "age": age, "acertos": 0, "erros": 0, "tempo": 0}
        self.save_users()
        if callback:
            callback(username, self.users[username])

    def validate_user(self, username, password):
        user = self.users.get(username)
        return user and user["password"] == password


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login e Registro")
        self.root.geometry("400x300")
        self.user_data_manager = UserDataManager()
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        self.label_username = tk.Label(self.frame, text="Usuário:")
        self.label_username.grid(row=0, column=0, sticky="e")
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.grid(row=0, column=1)

        self.label_password = tk.Label(self.frame, text="Senha:")
        self.label_password.grid(row=1, column=0, sticky="e")
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.grid(row=1, column=1)

        self.label_age = tk.Label(self.frame, text="Idade (registro):")
        self.label_age.grid(row=2, column=0, sticky="e")
        self.entry_age = tk.Entry(self.frame)
        self.entry_age.grid(row=2, column=1)

        self.btn_login = tk.Button(self.frame, text="Login", command=self.login)
        self.btn_login.grid(row=3, column=0, pady=10)

        self.btn_register = tk.Button(self.frame, text="Registrar", command=self.register)
        self.btn_register.grid(row=3, column=1, pady=10)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if self.user_data_manager.validate_user(username, password):
            messagebox.showinfo("Sucesso", f"Bem-vindo, {username}!")
            self.root.destroy()
            main_root = tk.Tk()
            app = MainApp(main_root, self.user_data_manager, username)
            main_root.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        age = self.entry_age.get()

        if not username or not password or not age:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        try:
            age_int = int(age)
            if age_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Idade deve ser um número inteiro positivo.")
            return

        def on_user_added(username, user_data):
            print(f"Novo usuário adicionado: {username}, dados: {user_data}")

        try:
            self.user_data_manager.add_user(username, password, age_int, callback=on_user_added)
            messagebox.showinfo("Sucesso", "Registro realizado com sucesso! Agora faça login.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))


class MainApp:
    def __init__(self, root, user_data_manager, current_user):
        self.root = root
        self.user_data_manager = user_data_manager
        self.users = self.user_data_manager.users
        self.current_user = current_user

        self.root.title("Programa de Inclusão Digital e Tecnológica")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")

        user_data = self.users.get(self.current_user, {"acertos": 0, "erros": 0, "tempo": 0})
        self.total_acertos = user_data.get("acertos", 0)
        self.total_erros = user_data.get("erros", 0)
        self.total_questoes = self.total_acertos + self.total_erros
        self.total_tempo_gasto = user_data.get("tempo", 0)

        self.start_time = None

        self.create_widgets()
        self.update_info_cards()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.user_data_manager.save_users()
        self.root.destroy()

    def create_widgets(self):
        sidebar = tk.Frame(self.root, bg="#34495e", width=250)
        sidebar.pack(side="left", fill="y")

        self.main_content = tk.Frame(self.root, bg="#ecf0f1")
        self.main_content.pack(side="right", expand=True, fill="both")

        title = tk.Label(self.main_content, text="Programa de Inclusão Digital e Tecnológica", font=("Arial", 20, "bold"), bg="#ecf0f1", fg="#2c3e50")
        title.pack(pady=20)

        self.cards_frame = tk.Frame(self.main_content, bg="#ecf0f1")
        self.cards_frame.pack(pady=10)

        self.card_total = self.create_info_card(self.cards_frame, "Total de Questões", 0)
        self.card_acertos = self.create_info_card(self.cards_frame, "Total de Acertos", 0)
        self.card_percentual = self.create_info_card(self.cards_frame, "Percentual de Acertos (%)", "0.00")
        self.card_media = self.create_info_card(self.cards_frame, "Média de Acertos (Geral)", "0.0")

        self.welcome_label = tk.Label(self.main_content, text="Bem-vindo ao programa! Use o menu à esquerda para navegar pelas lições.", font=("Arial", 14), bg="#ecf0f1", fg="#34495e", wraplength=450, justify="left")
        self.welcome_label.pack(pady=30, padx=20)

        # Botões
        btn_intro = tk.Button(sidebar, text="1. Introdução ao computador", width=28, command=self.introducao_computador, bg="#1abc9c", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#16a085")
        btn_intro.pack(pady=10, padx=10)

        btn_seg = tk.Button(sidebar, text="2. Segurança na internet", width=28, command=self.seguranca_internet, bg="#2980b9", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#2471a3")
        btn_seg.pack(pady=10, padx=10)

        btn_uso = tk.Button(sidebar, text="3. Uso básico de software", width=28, command=self.uso_basico_software, bg="#f39c12", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#d68910")
        btn_uso.pack(pady=10, padx=10)

        btn_dicas = tk.Button(sidebar, text="4. Dicas para inclusão digital", width=28, command=self.dicas_inclusao, bg="#8e44ad", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#7d3c98")
        btn_dicas.pack(pady=10, padx=10)

        btn_revisar = tk.Button(sidebar, text="5. Revisar todas as lições", width=28, command=self.revisar_todas, bg="#7f8c8d", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#707b7c")
        btn_revisar.pack(pady=10, padx=10)

        btn_resumo = tk.Button(sidebar, text="6. Mostrar resumo do desempenho", width=28, command=self.mostrar_resumo, bg="#34495e", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#2c3e50")
        btn_resumo.pack(pady=10, padx=10)

        self.add_graph_button(sidebar)

    def create_info_card(self, parent, title, value):
        card = tk.Frame(parent, bg="white", bd=2, relief="groove", width=200, height=100)
        card.pack(side="left", padx=5, pady=5, expand=True, fill="both")
        label_title = tk.Label(card, text=title, font=("Arial", 10, "bold"), bg="white", fg="#34495e")
        label_title.pack(pady=(10, 3))
        label_value = tk.Label(card, text=str(value), font=("Arial", 18, "bold"), bg="white", fg="#1abc9c")
        label_value.pack(pady=(0, 10))
        return label_value

    def update_info_cards(self):
        user_data = self.users.get(self.current_user, {"acertos": 0, "erros": 0, "tempo": 0})
        self.total_acertos = user_data.get("acertos", 0)
        self.total_erros = user_data.get("erros", 0)
        self.total_questoes = self.total_acertos + self.total_erros

        self.card_total.config(text=str(self.total_questoes))
        self.card_acertos.config(text=str(self.total_acertos))
        percentual = (self.total_acertos / self.total_questoes * 100) if self.total_questoes > 0 else 0
        self.card_percentual.config(text=f"{percentual:.2f}")

        acertos_list = [user.get("acertos", 0) for user in self.users.values()]
        media = statistics.mean(acertos_list) if acertos_list else 0
        self.card_media.config(text=f"{media:.2f}")
        self.user_data_manager.save_users()

    def add_graph_button(self, sidebar):
        btn_graficos = tk.Button(sidebar, text="7. Ver Gráficos Estatísticos", width=28, command=self.exibir_graficos, bg="#27ae60", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#229954")
        btn_graficos.pack(pady=10, padx=10)

    def exibir_graficos(self):
        acertos_all = [u.get("acertos", 0) for u in self.users.values() if u.get("acertos") is not None]
        erros_all = [u.get("erros", 0) for u in self.users.values() if u.get("erros") is not None]
        idades_all = [u.get("age", 0) for u in self.users.values() if u.get("age") is not None]

        window = tk.Toplevel(self.root)
        window.title("Gráficos Estatísticos")
        window.geometry("900x700")

        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Estatísticas dos Usuários Cadastrados", fontsize=16)

        if acertos_all:
            axs[0, 0].hist(acertos_all, bins=max(acertos_all) + 1, color='skyblue', edgecolor='black')
        else:
            axs[0, 0].text(0.5, 0.5, 'Sem dados', horizontalalignment='center', verticalalignment='center', transform=axs[0, 0].transAxes)
        axs[0, 0].set_title("Distribuição de Acertos")
        axs[0, 0].set_xlabel("Quantidade de Acertos")
        axs[0, 0].set_ylabel("Número de Usuários")

        if erros_all:
            axs[0, 1].hist(erros_all, bins=max(erros_all) + 1, color='salmon', edgecolor='black')
        else:
            axs[0, 1].text(0.5, 0.5, 'Sem dados', horizontalalignment='center', verticalalignment='center', transform=axs[0, 1].transAxes)
        axs[0, 1].set_title("Distribuição de Erros")
        axs[0, 1].set_xlabel("Quantidade de Erros")
        axs[0, 1].set_ylabel("Número de Usuários")

        if idades_all:
            axs[1, 0].hist(idades_all, bins=max(idades_all) // 5, color='lightgreen', edgecolor='black')
        else:
            axs[1, 0].text(0.5, 0.5, 'Sem dados', horizontalalignment='center', verticalalignment='center', transform=axs[1, 0].transAxes)
        axs[1, 0].set_title("Distribuição de Idades")
        axs[1, 0].set_xlabel("Idade")
        axs[1, 0].set_ylabel("Número de Usuários")

        if idades_all:
            age_counts = Counter(idades_all)
            ages = sorted(age_counts.keys())
            counts = [age_counts[age] for age in ages]
            axs[1, 1].bar(ages, counts, color='orange', edgecolor='black')
        else:
            axs[1, 1].text(0.5, 0.5, 'Sem dados', horizontalalignment='center', verticalalignment='center', transform=axs[1, 1].transAxes)
        axs[1, 1].set_title("Contagem de Usuários por Idade")
        axs[1, 1].set_xlabel("Idade")
        axs[1, 1].set_ylabel("Número de Usuários")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Estatísticas adicionais
        stats_frame = tk.Frame(window, bg="white", bd=2, relief="groove")
        stats_frame.pack(pady=10, padx=10, fill="x")

        if acertos_all:
            media_val = statistics.mean(acertos_all)
            mediana_val = statistics.median(acertos_all)
            try:
                moda_val = statistics.mode(acertos_all)
            except statistics.StatisticsError:
                moda_val = "N/A"
        else:
            media_val = mediana_val = moda_val = "Sem dados"

        tk.Label(stats_frame, text=f"Média de Acertos: {media_val}", font=("Arial", 12), bg="white").pack(pady=2)
        tk.Label(stats_frame, text=f"Mediana de Acertos: {mediana_val}", font=("Arial", 12), bg="white").pack(pady=2)
        tk.Label(stats_frame, text=f"Moda de Acertos: {moda_val}", font=("Arial", 12), bg="white").pack(pady=2)

        btn_salvar = tk.Button(window, text="Salvar Gráfico", command=lambda: self.salvar_grafico(fig))
        btn_salvar.pack(pady=10)

    def salvar_grafico(self, fig):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")], title="Salvar gráfico como")
        if file_path:
            fig.savefig(file_path)
            messagebox.showinfo("Salvar gráfico", f"Gráfico salvo em:\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()
