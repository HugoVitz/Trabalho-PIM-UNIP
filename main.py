import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import time

# --- user_data.py (Exemplo de implementação) ---
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

# --- Fim de user_data.py ---


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
            app = MainApp(main_root, self.user_data_manager, username) # Pass user_data_manager
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
        self.users = self.user_data_manager.users # Acesso aos dados de todos os usuários
        self.current_user = current_user

        self.root.title("Programa de Inclusão Digital e Tecnológica")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")

        # Inicializa os totais para o usuário atual
        user_data = self.users.get(self.current_user, {"acertos": 0, "erros": 0, "tempo": 0})
        self.total_acertos = user_data.get("acertos", 0)
        self.total_erros = user_data.get("erros", 0)
        self.total_questoes = self.total_acertos + self.total_erros
        self.total_tempo_gasto = user_data.get("tempo", 0)

        self.start_time = None

        self.create_widgets()
        self.update_info_cards()

        # Salva os dados do usuário ao fechar a janela principal
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
        self.card_mediana = self.create_info_card(self.cards_frame, "Mediana de Acertos (Geral)", "0.0")
        self.card_moda = self.create_info_card(self.cards_frame, "Moda de Acertos (Geral)", "0")

        self.welcome_label = tk.Label(self.main_content, text="Bem-vindo ao programa! Use o menu à esquerda para navegar pelas lições.", font=("Arial", 14), bg="#ecf0f1", fg="#34495e", wraplength=450, justify="left")
        self.welcome_label.pack(pady=30, padx=20)

        # Botões da barra lateral
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

        self.add_graph_button(sidebar) # Adiciona o botão de gráficos

    def create_info_card(self, parent, title, value):
        card = tk.Frame(parent, bg="white", bd=2, relief="groove", width=200, height=100)
        card.pack(side="left", padx=5, pady=5, expand=True, fill="both") # Ajuste padx/pady para mais cards

        label_title = tk.Label(card, text=title, font=("Arial", 10, "bold"), bg="white", fg="#34495e") # Fonte menor para caber
        label_title.pack(pady=(10,3))

        label_value = tk.Label(card, text=str(value), font=("Arial", 18, "bold"), bg="white", fg="#1abc9c") # Fonte menor
        label_value.pack(pady=(0,10))

        return label_value

    def update_info_cards(self):
        # Dados do usuário atual
        user_data = self.users.get(self.current_user, {"acertos": 0, "erros": 0, "tempo": 0})
        self.total_acertos = user_data.get("acertos", 0)
        self.total_erros = user_data.get("erros", 0)
        self.total_questoes = self.total_acertos + self.total_erros

        self.card_total.config(text=str(self.total_questoes))
        self.card_acertos.config(text=str(self.total_acertos))
        percentual = (self.total_acertos / self.total_questoes * 100) if self.total_questoes > 0 else 0
        self.card_percentual.config(text=f"{percentual:.2f}")

        # Estatísticas gerais de todos os usuários
        acertos_list = [user.get("acertos", 0) for user in self.users.values()]
        if acertos_list:
            media = statistics.mean(acertos_list)
            mediana = statistics.median(acertos_list)
            try:
                moda = statistics.mode(acertos_list)
            except statistics.StatisticsError:
                moda = "N/A" # Não há moda única
        else:
            media = mediana = moda = 0

        self.card_media.config(text=f"{media:.2f}")
        self.card_mediana.config(text=f"{mediana:.2f}")
        self.card_moda.config(text=str(moda))
        self.user_data_manager.save_users() # Salva os dados atualizados

    def ask_quiz(self, questions):
        score = 0
        start_time = time.time()
        for question_idx, (question, options, correct, explanation) in enumerate(questions):
            options_text = "\n".join([f"({key}) {value}" for key, value in options.items()])
            while True:
                answer = simpledialog.askstring("Quiz", f"Questão {question_idx+1}/{len(questions)}:\n\n{question}\n\n{options_text}\n\nEscolha a resposta correta:").strip().lower()
                if answer is None:
                    if messagebox.askyesno("Cancelar", "Deseja cancelar o quiz? Seu progresso nesta sessão será perdido."):
                        return score
                    else:
                        continue
                if answer in options:
                    break
                else:
                    messagebox.showerror("Erro", "Resposta inválida. Por favor, escolha uma das opções listadas (a, b, c...).")

            if answer == correct:
                messagebox.showinfo("Correto", "Correto!")
                score += 1
                self.users[self.current_user]["acertos"] += 1
            else:
                messagebox.showinfo("Incorreto", f"Incorreto. {explanation}")
                self.users[self.current_user]["erros"] += 1
        end_time = time.time()
        elapsed = end_time - start_time
        self.users[self.current_user]["tempo"] += elapsed
        self.update_info_cards() # Atualiza os cards após cada quiz
        return score

    def introducao_computador(self):
        info = (
            "Introdução ao Computador:\n"
            "Um computador é uma máquina que processa informações e executa programas.\n"
            "Ele é composto por hardware (partes físicas) e software (programas).\n"
            "Aprender a usar o computador é o primeiro passo para a inclusão digital."
        )
        messagebox.showinfo("Introdução ao Computador", info)
        questions = [
            ("O que é hardware?", {'a': 'Programas', 'b': 'Partes físicas', 'c': 'Dados'}, 'b', "Hardware são as partes físicas do computador."),
            ("Qual componente é considerado software?", {'a': 'Sistema operacional', 'b': 'Teclado', 'c': 'Monitor'}, 'a', "Software são os programas, como o sistema operacional."),
        ]
        self.ask_quiz(questions)

    def seguranca_internet(self):
        info = (
            "Segurança na Internet:\n"
            "1. Nunca compartilhe suas senhas.\n"
            "2. Use senhas fortes e diferentes para cada conta.\n"
            "3. Cuidado com e-mails e links suspeitos.\n"
            "4. Mantenha seu antivírus atualizado.\n"
            "5. Evite usar redes Wi-Fi públicas para transações importantes."
        )
        messagebox.showinfo("Segurança na Internet", info)
        questions = [
            ("Qual é uma boa prática para manter sua conta segura?", {'a': 'Compartilhar senhas', 'b': 'Usar senhas fortes', 'c': 'Ignorar atualizações'}, 'b', "Usar senhas fortes ajuda a proteger suas contas."),
            ("Por que evitar redes Wi-Fi públicas para transações importantes?", {'a': 'São lentas', 'b': 'Podem ser inseguras', 'c': 'São caras'}, 'b', "Redes públicas podem ser inseguras e expor seus dados."),
        ]
        self.ask_quiz(questions)

    def uso_basico_software(self):
        info = (
            "Uso Básico de Software:\n"
            "Aprenda a usar programas comuns como editores de texto, navegadores e aplicativos de mensagens.\n"
            "Pratique abrir, salvar e editar documentos.\n"
            "Explore tutoriais online para aprender mais sobre os programas que você usa."
        )
        messagebox.showinfo("Uso Básico de Software", info)
        questions = [
            ("Qual ação você deve fazer para salvar um documento?", {'a': 'Abrir', 'b': 'Salvar', 'c': 'Fechar'}, 'b', "Salvar é a ação para guardar seu documento."),
            ("Qual programa é usado para navegar na internet?", {'a': 'Editor de texto', 'b': 'Navegador', 'c': 'Planilha'}, 'b', "Navegadores são usados para acessar a internet."),
        ]
        self.ask_quiz(questions)

    def dicas_inclusao(self):
        info = (
            "Dicas para Inclusão Digital:\n"
            "1. Pratique regularmente para ganhar confiança.\n"
            "2. Participe de cursos e oficinas de informática.\n"
            "3. Peça ajuda a amigos ou familiares quando necessário.\n"
            "4. Use recursos acessíveis, como leitores de tela, se precisar.\n"
            "5. Mantenha-se atualizado com as novas tecnologias."
        )
        messagebox.showinfo("Dicas para Inclusao Digital", info)
        questions = [
            ("O que pode ajudar na inclusão digital?", {'a': 'Praticar regularmente', 'b': 'Ignorar a tecnologia', 'c': 'Evitar cursos'}, 'a', "Praticar regularmente ajuda a ganhar confiança."),
            ("Por que participar de cursos de informática?", {'a': 'Para aprender mais', 'b': 'Para perder tempo', 'c': 'Para evitar tecnologia'}, 'a', "Cursos ajudam a aprender e se atualizar."),
        ]
        self.ask_quiz(questions)

    def revisar_todas(self):
        messagebox.showinfo("Revisão", "Iniciando revisão de todas as lições. Prepare-se para os quizzes!")
        self.introducao_computador()
        self.seguranca_internet()
        self.uso_basico_software()
        self.dicas_inclusao()
        messagebox.showinfo("Revisão Concluída", "Você revisou todas as lições!")

    def mostrar_resumo(self):
        if self.total_questoes > 0:
            percentual = (self.total_acertos / self.total_questoes) * 100
            minutos = int(self.total_tempo_gasto // 60)
            segundos = int(self.total_tempo_gasto % 60)
            resumo = (
                f"Resumo do seu desempenho, {self.current_user}:\n\n"
                f"Total de questões respondidas: {self.total_questoes}\n"
                f"Total de acertos: {self.total_acertos}\n"
                f"Total de erros: {self.total_erros}\n"
                f"Percentual de acertos: {percentual:.2f}%\n"
                f"Tempo total gasto nos quizzes: {minutos} minutos e {segundos} segundos"
            )
        else:
            resumo = "Nenhuma questão respondida ainda. Comece uma lição para ver seu desempenho!"
        messagebox.showinfo("Resumo do seu desempenho", resumo)

    def add_graph_button(self, sidebar):
        btn_graficos = tk.Button(sidebar, text="7. Ver Gráficos Estatísticos", width=28, command=self.exibir_graficos, bg="#27ae60", fg="white", font=("Arial", 12, "bold"), bd=0, relief="flat", activebackground="#229954")
        btn_graficos.pack(pady=10, padx=10)

    def exibir_graficos(self):
        # Coleta os dados de todos os usuários
        acertos_all = [u.get("acertos", 0) for u in self.users.values() if u.get("acertos") is not None]
        erros_all = [u.get("erros", 0) for u in self.users.values() if u.get("erros") is not None]
        idades_all = [u.get("age", 0) for u in self.users.values() if u.get("age") is not None]

        # Cria uma nova janela para os gráficos
        window = tk.Toplevel(self.root)
        window.title("Gráficos Estatísticos")
        window.geometry("900x700") # Aumenta a altura para 4 subplots

        fig, axs = plt.subplots(2, 2, figsize=(12, 10)) # Organiza em 2 linhas, 2 colunas
        fig.suptitle("Estatísticas dos Usuários Cadastrados", fontsize=16)

        # Gráfico 1: Histograma de Acertos
        if acertos_all:
            axs[0, 0].hist(acertos_all, bins=max(acertos_all) + 1 if acertos_all else 1, color='skyblue', edgecolor='black')
        else:
            axs[0, 0].text(0.5, 0.5, 'Sem dados', horizontalalignment='center', verticalalignment='center', transform=axs[0, 0].transAxes)
        axs[0, 0].set_title("Distribuição de Acertos")
        axs[0, 0].set_xlabel("Quantidade de Acertos")
        axs[0, 0].set_ylabel("Número de Usuários")
        axs[0, 0].set_xticks(range(max(acertos_all) + 1)) # Garante ticks inteiros no eixo X

        # Gráfico 2: Histograma de Erros
        if erros_all:
            axs[0, 1].hist(erros_all, bins=max(erros_all) + 1 if erros_all else 1, color='salmon', edgecolor='black')
        else:
            axs[0, 1].text(0.5, 0.5, 'Sem dados', horizontalalignment='center', verticalalignment='center', transform=axs[0, 1].transAxes)
        axs[0, 1].set_title("Distribuição de Erros")
        axs[0, 1].set_xlabel("Quantidade de Erros")
        axs[0, 1].set_ylabel("Número de Usuários")
        axs[0, 1].set_xticks(range(max(erros_all) + 1)) # Garante ticks inteiros no eixo X


        # Gráfico 3: Histograma de Idades
        if idades_all:
            axs[1, 0].hist(idades_all, bins=max(idades_all) // 5 if idades_all else 1, color='lightgreen', edgecolor='black') # Bins por faixa de 5 anos
        else:
            axs[1, 0].text(0.5, 0.5, 'Sem dados', horizontalalignment='center', verticalalignment='center', transform=axs[1, 0].transAxes)
        axs[1, 0].set_title("Distribuição de Idades")
        axs[1, 0].set_xlabel("Idade")
        axs[1, 0].set_ylabel("Número de Usuários")

        # Gráfico 4: Distribuição de Idades (Barras)
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
        axs[1, 1].set_xticks(ages) # Garante ticks para cada idade presente

        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Ajusta layout para evitar sobreposição

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Botão para salvar o gráfico dentro da janela de gráficos
        btn_salvar = tk.Button(window, text="Salvar Gráfico", command=lambda: self.salvar_grafico(fig))
        btn_salvar.pack(pady=10)

    def salvar_grafico(self, fig):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                                 title="Salvar gráfico como")
        if file_path:
            fig.savefig(file_path)
            messagebox.showinfo("Salvar gráfico", f"Gráfico salvo em:\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()