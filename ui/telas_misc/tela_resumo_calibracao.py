import tkinter as tk
from tkinter import ttk
from controllers.equipamento_controller import quantidade_calibr

class TelaResumoCalibracao(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)

        # Consulta os dados de calibração
        total, calibrado, nao_calibrado, incerto, especial = quantidade_calibr()

        # Configuração da janela
        self.title("Resumo de Calibração")
        self.configure(bg="#F5F1E9")
        self.resizable(False, False)

        # Posiciona a janela próxima à janela principal, se master existir
        if master is not None:
            master.update_idletasks()
            x = master.winfo_x() + 50
            y = master.winfo_y() + 50
            self.geometry(f"+{x}+{y}")

        # Frame principal
        frame_principal = tk.Frame(self, bg="#FDFCF8", bd=2, relief="groove", padx=20, pady=20)
        frame_principal.pack(padx=40, pady=20)

        # Título
        tk.Label(frame_principal, text="Resumo de Calibração (Ativos)", font=("Courier New", 16, "bold"),
                 bg="#FDFCF8", fg="#333333").pack(pady=(0, 15))

        # Frame de informações
        info_frame = tk.Frame(frame_principal, bg="#FDFCF8")
        info_frame.pack(pady=(0, 15), padx=15)

        # Dados
        dados = [
            ("Total de Equipamentos:", total, "#FFFFFF"),
            ("Calibrados:", calibrado, "#A7E9AF"),
            ("Não Calibrados:", nao_calibrado, "#FFB3B3"),
            ("Incertos:", incerto, "#DBDBDB"),
            ("Especiais:", especial, "#A9CCE3"),
        ]

        for i, (texto, valor, cor) in enumerate(dados):
            tk.Label(info_frame, text=texto, font=("Courier New", 12),
                     bg="#FDFCF8", fg="#333333").grid(row=i, column=0, sticky="w", padx=(0, 10), pady=(5 if i > 0 else 0, 0))
            tk.Label(info_frame, text=str(valor), font=("Courier New", 12, "bold"),
                     bg=cor, fg="#333333", width=8, relief="sunken", bd=2).grid(row=i, column=1, sticky="w", pady=(5 if i > 0 else 0, 0))

        # Separador
        ttk.Separator(frame_principal, orient="horizontal").pack(fill="x", pady=10)

        # Botão de fechar
        tk.Button(frame_principal, text="Fechar", command=self.destroy,
                  font=("Courier New", 12), bg="#C85A17", fg="white",
                  activebackground="#E38B2B", activeforeground="white",
                  relief="raised", bd=3, padx=20, pady=5).pack(pady=(10, 0))

        # Modal
        self.grab_set()
        self.wait_window(self)
