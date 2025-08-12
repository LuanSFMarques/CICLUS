import tkinter as tk
from tkinter import ttk, messagebox
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

        largura = 500
        altura = 350

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

        label("Tipo de Item:").pack(anchor="w", padx=pad_x, pady=(pad_y, 2))

        self.combo_tipo = ttk.Combobox(
            self,
            values=[desc for _, desc in tipos_item],
            state="readonly",
            font=("Courier New", 11)
        )
        self.combo_tipo.pack(padx=pad_x, pady=(0, pad_y))
        self.combo_tipo.current(0)

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

        btn_frame = tk.Frame(self, bg="#F5F1E9")
        btn_frame.pack(pady=20)

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

        if not data_evento:
            data_evento_formatada = datetime.today().strftime("%Y-%m-%d")
        else:
            formatos_suportados = ["%d-%m-%Y", "%d/%m/%Y"]
            for formato in formatos_suportados:
                try:
                    data_evento_formatada = datetime.strptime(data_evento, formato).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    data_evento_formatada = None
            
            if not data_evento_formatada:
                messagebox.showerror("Erro", "Data inválida! Use o formato DD-MM-YYYY ou DD/MM/YYYY.")
                return

        dados = {
            "equipamento_id": self.equipamento_id,
            "tipo_item_id": tipo_id,
            "descricao": descricao,
            "data_evento": data_evento_formatada
        }

        if tipo_id in (1, 2):
            escolha = tk.Toplevel(self)
            escolha.title("Selecionar Novo Valor")
            escolha.configure(bg="#F5F1E9")

            largura_escolha = 600
            altura_escolha = 150
            pos_x = self.winfo_rootx() + 50
            pos_y = self.winfo_rooty() + 50
            escolha.geometry(f"{largura_escolha}x{altura_escolha}+{pos_x}+{pos_y}")

            tk.Label(escolha, text="Selecione o novo valor para atualização automática de metadado:",
                    bg="#F5F1E9", font=("Courier New", 11, "bold")).pack(pady=10)

            valores = tipos_status if tipo_id == 1 else tipos_setor
            combo = ttk.Combobox(escolha, values=[v[1] for v in valores],
                                state="readonly", font=("Courier New", 11))
            combo.pack(pady=5)
            combo.current(0)

            def confirmar():
                nome_selecionado = combo.get()
                id_selecionado = next((v[0] for v in valores if v[1] == nome_selecionado), None)
                if tipo_id == 1:
                    dados["novo_status"] = id_selecionado
                elif tipo_id == 2:
                    dados["novo_setor"] = id_selecionado
                escolha.destroy()
                self.finalizar_criacao(dados)

            tk.Button(escolha, text="Confirmar", bg="#C85A17", fg="white",
                    font=("Courier New", 11, "bold"), command=confirmar).pack(pady=10)

            escolha.transient(self)
            escolha.grab_set()
            self.wait_window(escolha)
        else:
            self.finalizar_criacao(dados)


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

