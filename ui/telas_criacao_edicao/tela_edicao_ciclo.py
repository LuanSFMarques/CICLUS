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

        if master is not None:
            pos_x = master.winfo_x() + 50
            pos_y = master.winfo_y() + 50
            self.geometry(f"500x400+{pos_x}+{pos_y}")
        else:
            self.geometry("500x400")

        self.item = obter_item_ciclo_vida_por_id(item_id)
        if not self.item:
            messagebox.showerror("Erro", "Item não encontrado.")
            self.destroy()
            return

        tk.Label(self, text="Tipo do Item:", bg="#F5F1E9", font=("Courier New", 12)).pack(pady=5)
        tk.Label(self, text=self.item['tipo_item'], bg="#F5F1E9", font=("Courier New", 11, "bold")).pack(pady=5)

        self.tipo_id_original = next((t[0] for t in tipos_item if t[1] == self.item['tipo_item']), None)

        # Descrição
        tk.Label(self, text="Descrição:", bg="#F5F1E9", font=("Courier New", 12)).pack(pady=5)
        self.txt_descricao = tk.Text(self, height=6, width=50)
        self.txt_descricao.pack(pady=5)
        self.txt_descricao.insert("1.0", self.item["descricao"])

        # Data
        tk.Label(self, text="Data (DD-MM-YYYY ou DD/MM/YYYY):", bg="#F5F1E9", font=("Courier New", 12)).pack(pady=5)
        self.entry_data = tk.Entry(self)
        self.entry_data.pack(pady=5)

        try:
            data_dt = datetime.strptime(self.item["data"], "%Y-%m-%d")
            data_formatada = data_dt.strftime("%d-%m-%Y")
        except ValueError:
            data_formatada = self.item["data"]

        self.entry_data.insert(0, data_formatada)

        # Botão salvar
        btn_salvar = tk.Button(
            self,
            text="Salvar Alterações",
            command=self.salvar,
            bg="#C85A17",
            fg="white",
            font=("Courier New", 12, "bold")
        )
        btn_salvar.pack(pady=20)

    def salvar(self):
        descricao = self.txt_descricao.get("1.0", "end").strip()
        data_digitada = self.entry_data.get().strip()

        formatos_suportados = ["%d-%m-%Y", "%d/%m/%Y"]
        data_formatada = None
        for formato in formatos_suportados:
            try:
                data_formatada = datetime.strptime(data_digitada, formato).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

        if not data_formatada:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD-MM-YYYY ou DD/MM/YYYY.")
            return

        confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente salvar as alterações?")
        if not confirmacao:
            return

        try:
            atualizar_item_ciclo_vida(self.item_id, self.tipo_id_original, descricao, data_formatada)
            messagebox.showinfo("Sucesso", "Item atualizado com sucesso.")
            log_msg(f"Item Editado: '{self.item_id}'")
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar item:\n{e}")
