import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from controllers.itens_controller import obter_item_ciclo_vida_por_id, atualizar_item_ciclo_vida
from helpers import log_msg
from data.tipos import tipos_item

class TelaEdicaoCiclo(tk.Toplevel):
    def __init__(self, master, item_id, callback=None):
        super().__init__(master)
        self.item_id = item_id
        self.callback = callback
        self.configure(bg="#F5F1E9")
        self.title("Editar Item do Ciclo de Vida")
        self.resizable(False, False)

        largura = 550
        altura = 500  # aumentada para novos campos
        if master is not None:
            pos_x = master.winfo_x() + 50
            pos_y = master.winfo_y() + 50
            self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        else:
            self.geometry(f"{largura}x{altura}")

        # Carrega item
        self.item = obter_item_ciclo_vida_por_id(item_id)
        if not self.item:
            messagebox.showerror("Erro", "Item não encontrado.")
            self.destroy()
            return

        # Tipo do item
        tk.Label(self, text="Tipo do Item:", bg="#F5F1E9", font=("Courier New", 12)).pack(anchor="w", padx=15, pady=(10,2))
        tk.Label(self, text=self.item['tipo_item'], bg="#F5F1E9", font=("Courier New", 11, "bold")).pack(anchor="w", padx=15)

        self.tipo_id_original = next((t[0] for t in tipos_item if t[1] == self.item['tipo_item']), None)

        # Descrição
        tk.Label(self, text="Descrição:", bg="#F5F1E9", font=("Courier New", 12)).pack(anchor="w", padx=15, pady=(10,2))
        self.txt_descricao = tk.Text(self, height=5, width=50, font=("Courier New", 11))
        self.txt_descricao.pack(padx=15, pady=(0,10))
        self.txt_descricao.insert("1.0", self.item["descricao"])

        # Data
        tk.Label(self, text="Data (DD-MM-YYYY ou DD/MM/YYYY):", bg="#F5F1E9", font=("Courier New", 12)).pack(anchor="w", padx=15, pady=(10,2))
        self.entry_data = tk.Entry(self, font=("Courier New", 11))
        self.entry_data.pack(padx=15, pady=(0,10))
        try:
            data_dt = datetime.strptime(self.item["data"], "%Y-%m-%d")
            self.entry_data.insert(0, data_dt.strftime("%d-%m-%Y"))
        except:
            self.entry_data.insert(0, self.item["data"])

        # Fornecedor
        tk.Label(self, text="Fornecedor:", bg="#F5F1E9", font=("Courier New", 12)).pack(anchor="w", padx=15, pady=(10,2))
        self.entry_fornecedor = tk.Entry(self, font=("Courier New", 11), width=40)
        self.entry_fornecedor.pack(padx=15, pady=(0,10))
        self.entry_fornecedor.insert(0, self.item.get("fornecedor") or "")

        # Valor
        tk.Label(self, text="Valor (R$):", bg="#F5F1E9", font=("Courier New", 12)).pack(anchor="w", padx=15, pady=(10,2))
        self.entry_valor = tk.Entry(self, font=("Courier New", 11), width=20)
        self.entry_valor.pack(padx=15, pady=(0,10))
        if self.item.get("valor") is not None:
            self.entry_valor.insert(0, f"{self.item['valor']:.2f}")

        # Botão salvar
        btn_salvar = tk.Button(
            self,
            text="Salvar Alterações",
            bg="#C85A17",
            fg="white",
            font=("Courier New", 12, "bold"),
            command=self.salvar
        )
        btn_salvar.pack(pady=15)

    def salvar(self):
        descricao = self.txt_descricao.get("1.0", "end").strip()
        data_digitada = self.entry_data.get().strip()

        # Validação de data
        formatos_suportados = ["%d-%m-%Y", "%d/%m/%Y"]
        data_formatada = None
        for formato in formatos_suportados:
            try:
                data_formatada = datetime.strptime(data_digitada, formato).strftime("%Y-%m-%d")
                break
            except:
                continue
        if not data_formatada:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD-MM-YYYY ou DD/MM/YYYY.")
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

        # Fornecedor
        fornecedor = self.entry_fornecedor.get().strip()
        if fornecedor == "":
            fornecedor = None

        confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente salvar as alterações?")
        if not confirmacao:
            return

        try:
            atualizar_item_ciclo_vida(
                self.item_id,
                self.tipo_id_original,
                descricao,
                data_formatada,
                fornecedor,
                valor
            )
            messagebox.showinfo("Sucesso", "Item atualizado com sucesso.")
            log_msg(f"Item Editado: '{self.item_id}'")
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar item:\n{e}")
