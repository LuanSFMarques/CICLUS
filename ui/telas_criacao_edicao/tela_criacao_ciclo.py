import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from controllers.itens_controller import criar_item_ciclo_vida
from helpers import log_msg
from data.tipos import tipos_item, tipos_setor, tipos_status

class TelaCriacaoCiclo(tk.Toplevel):
    def __init__(self, master, equipamento_id, callback_atualizar=None):
        super().__init__(master)
        self.title("Adicionar Item ao Ciclo de Vida")
        self.configure(bg="#F5F1E9")
        self.resizable(False, False)

        largura = 550
        altura = 500  # aumentado para caber novos campos

        if master is not None:
            master_x = master.winfo_x()
            master_y = master.winfo_y()
            pos_x = master_x + 50
            pos_y = master_y + 50
            self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        else:
            self.geometry(f"{largura}x{altura}")

        self.equipamento_id = equipamento_id
        self.callback_atualizar = callback_atualizar

        self.criar_widgets()

    def criar_widgets(self):
        pad_x = 15
        pad_y = 8

        def label(texto):
            return tk.Label(
                self,
                text=texto,
                bg="#F5F1E9",
                fg="#333333",
                font=("Courier New", 11, "bold")
            )

        # Tipo de Item
        label("Tipo de Item:").pack(anchor="w", padx=pad_x, pady=(pad_y, 2))
        self.combo_tipo = ttk.Combobox(
            self,
            values=[desc for _, desc in tipos_item],
            state="readonly",
            font=("Courier New", 11)
        )
        self.combo_tipo.pack(padx=pad_x, pady=(0, pad_y))
        self.combo_tipo.current(0)

        # Descrição
        label("Descrição:").pack(anchor="w", padx=pad_x, pady=(pad_y, 2))
        self.text_descricao = tk.Text(
            self,
            width=50,
            height=5,
            font=("Courier New", 11),
            bg="#FFFFFF",
            fg="#333333",
            relief="sunken",
            bd=1,
            insertbackground="#333333",
            wrap="word"
        )
        self.text_descricao.pack(padx=pad_x, pady=(0, pad_y))

        # Data do Evento
        label("Data do Evento (DD-MM-YYYY):").pack(anchor="w", padx=pad_x, pady=(pad_y, 2))
        self.entry_data = tk.Entry(
            self,
            width=20,
            font=("Courier New", 11),
            bg="#FFFFFF",
            fg="#333333",
            relief="sunken",
            bd=1,
            insertbackground="#333333"
        )
        self.entry_data.pack(padx=pad_x, pady=(0, pad_y))

        # Fornecedor
        label("Fornecedor:").pack(anchor="w", padx=pad_x, pady=(pad_y, 2))
        self.entry_fornecedor = tk.Entry(
            self,
            width=40,
            font=("Courier New", 11),
            bg="#FFFFFF",
            fg="#333333",
            relief="sunken",
            bd=1,
            insertbackground="#333333"
        )
        self.entry_fornecedor.pack(padx=pad_x, pady=(0, pad_y))

        # Valor
        label("Valor (R$):").pack(anchor="w", padx=pad_x, pady=(pad_y, 2))
        self.entry_valor = tk.Entry(
            self,
            width=20,
            font=("Courier New", 11),
            bg="#FFFFFF",
            fg="#333333",
            relief="sunken",
            bd=1,
            insertbackground="#333333"
        )
        self.entry_valor.pack(padx=pad_x, pady=(0, pad_y))

        # Botões
        btn_frame = tk.Frame(self, bg="#F5F1E9")
        btn_frame.pack(pady=15)

        btn_salvar = tk.Button(
            btn_frame,
            text="Salvar",
            bg="#C85A17",
            fg="white",
            font=("Courier New", 13, "bold"),
            relief="raised",
            bd=3,
            activebackground="#E38B2B",
            activeforeground="white",
            command=self.salvar_item,
            width=12
        )
        btn_salvar.pack(side="left", padx=20)

        btn_cancelar = tk.Button(
            btn_frame,
            text="Cancelar",
            bg="#8B8B8B",
            fg="white",
            font=("Courier New", 13, "bold"),
            relief="raised",
            bd=3,
            activebackground="#A9A9A9",
            activeforeground="white",
            command=self.destroy,
            width=12
        )
        btn_cancelar.pack(side="left", padx=20)

    def salvar_item(self):
        tipo_index = self.combo_tipo.current()
        tipo_id = tipos_item[tipo_index][0]

        descricao = self.text_descricao.get("1.0", "end").strip()
        data_evento = self.entry_data.get().strip()

        # Validação de data
        if not data_evento:
            data_evento_formatada = datetime.today().strftime("%Y-%m-%d")
        else:
            formatos_suportados = ["%d-%m-%Y", "%d/%m/%Y"]
            data_evento_formatada = None
            for formato in formatos_suportados:
                try:
                    data_evento_formatada = datetime.strptime(data_evento, formato).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            if not data_evento_formatada:
                messagebox.showerror("Erro", "Data inválida! Use o formato DD-MM-YYYY ou DD/MM/YYYY.")
                return

        # Validação de valor monetário
        valor_str = self.entry_valor.get().strip().replace(",", ".")
        if valor_str == "":
            valor = None
        else:
            try:
                valor_float = float(valor_str)
                if round(valor_float, 2) != valor_float:
                    raise ValueError
                valor = round(valor_float, 2)
            except ValueError:
                messagebox.showerror("Valor inválido", "Digite um valor válido (ex: 123 ou 123.45 com até 2 casas decimais).")
                self.entry_valor.focus_set()
                return

        fornecedor = self.entry_fornecedor.get().strip()
        if fornecedor == "":
            fornecedor = None

        dados = {
            "equipamento_id": self.equipamento_id,
            "tipo_item_id": tipo_id,
            "descricao": descricao,
            "data_evento": data_evento_formatada,
            "fornecedor": fornecedor,
            "valor": valor
        }

        # 🔹 Coletar info extra para tipo 1 ou 2
        if tipo_id == 1:  # mudança de status
            escolha = self.selecionar_opcao("Selecione o novo Status", tipos_status)
            if escolha is None:
                return
            dados["novo_status"] = escolha
        elif tipo_id == 2:  # troca de setor
            escolha = self.selecionar_opcao("Selecione o novo Setor", tipos_setor)
            if escolha is None:
                return
            dados["novo_setor"] = escolha

        self.finalizar_criacao(dados)

    def selecionar_opcao(self, titulo, opcoes):
        """Abre uma janela simples com combobox para escolha."""
        dialog = tk.Toplevel(self)
        dialog.title(titulo)
        dialog.grab_set()
        dialog.configure(bg="#F5F1E9")

        largura = 300
        altura = 150

        # Pega posição da janela pai (self)
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()

        # Define a posição relativa no mesmo monitor
        pos_x = parent_x + 50
        pos_y = parent_y + 50

        dialog.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(dialog, text=titulo, bg="#F5F1E9", font=("Courier New", 11, "bold")).pack(pady=10)

        combo = ttk.Combobox(dialog, values=[desc for _, desc in opcoes], state="readonly", font=("Courier New", 11))
        combo.pack(pady=5)
        combo.current(0)

        escolha = {"valor": None}

        def confirmar():
            idx = combo.current()
            escolha["valor"] = opcoes[idx][0]
            dialog.destroy()

        btn = tk.Button(dialog, text="Confirmar", command=confirmar, bg="#C85A17", fg="white", width=12)
        btn.pack(pady=10)

        dialog.wait_window()
        return escolha["valor"]


    def finalizar_criacao(self, dados):
        confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente criar este item do ciclo de vida?")
        if not confirmacao:
            return
        try:
            criar_item_ciclo_vida(dados)
            messagebox.showinfo("Sucesso", "Item adicionado com sucesso.")
            log_msg(f"Item Criado: '{dados['tipo_item_id']}' -> '{self.equipamento_id}'")
            self.destroy()
            if self.callback_atualizar:
                self.callback_atualizar()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar item:\n{e}")
