import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from controllers.equipamento_controller import obter_equipamento_cru, atualizar_equipamento
from data.tipos import tipos_eq, tipos_setor, tipos_status, tipos_status_calibr
from helpers import log_msg


class TelaEdicaoEquipamento(tk.Toplevel):
    def __init__(self, equip_id, master=None):
        super().__init__(master)
        self.title(f"Editar Equipamento - ID {equip_id}")
        self.resizable(False, False)
        self.equip_id = equip_id
        self.equipamento = obter_equipamento_cru(equip_id)

        if not self.equipamento:
            messagebox.showerror("Erro", "Equipamento não encontrado.")
            self.destroy()
            return

        if master is not None:
            pos_x = master.winfo_x() + 50
            pos_y = master.winfo_y() + 50
            self.geometry(f"500x600+{pos_x}+{pos_y}")
        else:
            self.geometry("500x600")

        self.configure(bg="#F5F1E9")
        self.criar_widgets()
        self.preencher_campos()

    def criar_widgets(self):
        self.campos = {}

        def label(parent, text):
            return tk.Label(parent, text=text, bg="#F5F1E9", fg="#333333", font=("Courier New", 11, "bold"))

        container = tk.Frame(self, bg="#F5F1E9")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#F5F1E9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(canvas, bg="#F5F1E9")
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-int(e.delta / 120), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Campos
        campos = [
            ("Nome do Equipamento", "nome_eq"),
            ("Tipo do Equipamento", "tipo_eq_id", tipos_eq),
            ("Setor", "setor_id", [s[1] for s in tipos_setor]),
            ("Status", "status_id", [s[1] for s in tipos_status]),
            ("Data de Aquisição (DD-MM-YYYY)", "data_aquisicao"),
            ("Última Calibração (DD-MM-YYYY)", "ultima_calibracao"),
            ("Periodicidade (meses)", "periodicidade"),
            ("Status de Calibração", "status_calibracao_id", [s[1] for s in tipos_status_calibr]),
            ("Fabricante", "fabricante"),
            ("Modelo", "modelo"),
            ("Modelo Técnico", "modelo_tecnico"),
            ("Número de Série", "numero_serie"),
            ("Informações Extras", "extra_info")
        ]

        for texto, chave, *opcoes in campos:
            label(self.scroll_frame, texto).pack(anchor="w", padx=15, pady=(8, 2))
            if opcoes:
                combo = ttk.Combobox(self.scroll_frame, values=opcoes[0], state="readonly", font=("Courier New", 11))
                combo.pack(padx=15, pady=(0, 8))
                self.campos[chave] = combo
            elif chave == "extra_info":
                text = tk.Text(self.scroll_frame, height=4, width=50, font=("Courier New", 11))
                text.pack(padx=15, pady=(0, 8))
                self.campos[chave] = text
            else:
                entry = tk.Entry(self.scroll_frame, font=("Courier New", 11), width=50)
                entry.pack(padx=15, pady=(0, 8))
                self.campos[chave] = entry

        btn_frame = tk.Frame(self.scroll_frame, bg="#F5F1E9")
        btn_frame.pack(pady=25)

        tk.Button(
            btn_frame, text="Salvar Alterações", command=self.salvar, bg="#C85A17",
            fg="white", font=("Courier New", 13, "bold"), width=18
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame, text="Cancelar", command=self.destroy, bg="#8B8B8B",
            fg="white", font=("Courier New", 13, "bold"), width=12
        ).pack(side="left", padx=10)

    def preencher_campos(self):
        e = self.equipamento

        def get_nome_por_id(lista, id_):
            return next((nome for ident, nome in lista if ident == id_), "")

        self.campos["nome_eq"].insert(0, e["nome_eq"])
        self.campos["tipo_eq_id"].set(tipos_eq[e["tipo_eq_id"] - 1] if e["tipo_eq_id"] else "")
        self.campos["setor_id"].set(get_nome_por_id(tipos_setor, e["setor_id"]))
        self.campos["status_id"].set(get_nome_por_id(tipos_status, e["status_id"]))
        self.campos["data_aquisicao"].insert(0, self.formatar_data(e["data_aquisicao"]))
        self.campos["ultima_calibracao"].insert(0, self.formatar_data(e["ultima_calibracao"]))
        self.campos["periodicidade"].insert(0, str(e["periodicidade"]))
        self.campos["status_calibracao_id"].set(get_nome_por_id(tipos_status_calibr, e["status_calibracao_id"]))
        self.campos["fabricante"].insert(0, e["fabricante"])
        self.campos["modelo"].insert(0, e["modelo"])
        self.campos["modelo_tecnico"].insert(0, e["modelo_tecnico"])
        self.campos["numero_serie"].insert(0, e["numero_serie"])
        self.campos["extra_info"].insert("1.0", e["extra_info"])

    def formatar_data(self, data_str):
        if not data_str:
            return ""
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d-%m-%Y")

    def salvar(self):
        try:
            nome = self.campos["nome_eq"].get().strip()
            sigla = nome.split("-")[0] if "-" in nome else ""
            data_aq = self.converter_data(self.campos["data_aquisicao"].get().strip())
            ultima_cal = self.converter_data(self.campos["ultima_calibracao"].get().strip())
            periodicidade = int(self.campos["periodicidade"].get().strip()) if self.campos["periodicidade"].get().strip().isdigit() else None

            novos_dados = {
                "nome_eq": nome,
                "tipo_eq_id": tipos_eq.index(self.campos["tipo_eq_id"].get()) + 1,
                "sigla_eq": sigla,
                "setor_id": next((i for i, nome in tipos_setor if nome == self.campos["setor_id"].get()), None),
                "status_id": next((i for i, nome in tipos_status if nome == self.campos["status_id"].get()), None),
                "data_aquisicao": data_aq,
                "ultima_calibracao": ultima_cal,
                "periodicidade": periodicidade,
                "status_calibracao_id": next((i for i, nome in tipos_status_calibr if nome == self.campos["status_calibracao_id"].get()), None),
                "fabricante": self.campos["fabricante"].get().strip(),
                "modelo": self.campos["modelo"].get().strip(),
                "modelo_tecnico": self.campos["modelo_tecnico"].get().strip(),
                "numero_serie": self.campos["numero_serie"].get().strip(),
                "extra_info": self.campos["extra_info"].get("1.0", "end").strip()
            }

            confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente salvar as alterações?")
            if not confirmacao:
                return

            atualizar_equipamento(self.equip_id, novos_dados)  # Agora usa ID, não SOND_ID
            messagebox.showinfo("Sucesso", "Equipamento atualizado com sucesso!")
            log_msg(f"Equipamento Editado: '{nome}'")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def converter_data(self, data_str):
        for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(data_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = TelaEdicaoEquipamento(equip_id=1, master=root)
    app.mainloop()
