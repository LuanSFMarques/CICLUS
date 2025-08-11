import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from controllers.equipamento_controller import criar_equipamento
from data.tipos import tipos_eq, tipos_setor, tipos_status, tipos_status_calibr
from helpers import log_msg


class TelaCriacaoEquipamento(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Criar Novo Equipamento")
        self.resizable(False, False)

        if master is not None:
            master_x = master.winfo_x()
            master_y = master.winfo_y()
            pos_x = master_x + 50
            pos_y = master_y + 50
            self.geometry(f"500x600+{pos_x}+{pos_y}")
        else:
            self.geometry("500x600")

        self.configure(bg="#F5F1E9")
        self.criar_widgets()

    def criar_widgets(self):
        pad_x = 15
        pad_y = 8

        def label(parent, text):
            return tk.Label(
                parent,
                text=text,
                bg="#F5F1E9",
                fg="#333333",
                font=("Courier New", 11, "bold")
            )

        container = tk.Frame(self, bg="#F5F1E9")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#F5F1E9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        scroll_frame = tk.Frame(canvas, bg="#F5F1E9")
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def on_enter(event):
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-int(e.delta / 120), "units"))

        def on_leave(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        campos = [
            ("Nome do Equipamento:", 50, "entry_nome"),
            ("Tipo do Equipamento:", None, "combo_tipo"),
            ("Setor:", None, "combo_setor"),
            ("Status:", None, "combo_status"),
            ("SOND ID (Número único):", 20, "entry_sond"),
            ("Data de Aquisição (DD-MM-YYYY):", 20, "entry_data_aq"),
            ("Última Calibração (DD-MM-YYYY):", 20, "entry_ultima_cal"),
            ("Periodicidade (meses):", 10, "entry_periodicidade"),
            ("Status de Calibração:", None, "combo_status_calibr"),
            ("Fabricante:", 30, "entry_fabricante"),
            ("Modelo:", 30, "entry_modelo"),
            ("Modelo Técnico:", 30, "entry_modelo_tecnico"),
            ("Número de Série:", 30, "entry_num_serie"),
            ("Informações Extras:", (50, 4), "text_extra_info")
        ]

        for texto, tamanho, nome_atributo in campos:
            label(scroll_frame, texto).pack(anchor="w", padx=pad_x, pady=(pad_y, 2))

            if nome_atributo.startswith("entry_"):
                entry = tk.Entry(
                    scroll_frame,
                    width=tamanho,
                    font=("Courier New", 11),
                    bg="#FFFFFF",
                    fg="#333333",
                    relief="sunken",
                    bd=1,
                    insertbackground="#333333"
                )
                entry.pack(padx=pad_x, pady=(0, pad_y))
                setattr(self, nome_atributo, entry)

            elif nome_atributo.startswith("combo_"):
                values = []
                if nome_atributo == "combo_tipo":
                    values = tipos_eq
                elif nome_atributo == "combo_setor":
                    values = [s[1] for s in tipos_setor]
                elif nome_atributo == "combo_status":
                    values = [s[1] for s in tipos_status]
                elif nome_atributo == "combo_status_calibr":
                    values = [s[1] for s in tipos_status_calibr]

                combo = ttk.Combobox(scroll_frame, values=values, state="readonly", font=("Courier New", 11))
                combo.pack(padx=pad_x, pady=(0, pad_y))
                combo.current(0)
                setattr(self, nome_atributo, combo)

            elif nome_atributo == "text_extra_info":
                largura, altura = tamanho
                text = tk.Text(
                    scroll_frame,
                    width=largura,
                    height=altura,
                    font=("Courier New", 11),
                    bg="#FFFFFF",
                    fg="#333333",
                    relief="sunken",
                    bd=1,
                    insertbackground="#333333",
                    wrap="word"
                )
                text.pack(padx=pad_x, pady=(0, pad_y))
                setattr(self, nome_atributo, text)

        # Botões
        btn_frame = tk.Frame(scroll_frame, bg="#F5F1E9")
        btn_frame.pack(pady=25)

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
            command=self.salvar_equipamento,
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

    def salvar_equipamento(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get().strip()
        setor = self.combo_setor.get().strip()
        status = self.combo_status.get().strip()
        sond_id_raw = self.entry_sond.get().strip()
        data_aquisicao_br = self.entry_data_aq.get().strip()
        ultima_calibracao_br = self.entry_ultima_cal.get().strip()
        periodicidade_raw = self.entry_periodicidade.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Nome do equipamento é obrigatório!")
            return

        if "-" not in nome:
            messagebox.showerror("Erro", "Nome do equipamento deve conter um '-' para gerar a sigla!")
            return

        if not tipo:
            messagebox.showerror("Erro", "Tipo do equipamento é obrigatório!")
            return

        if not setor:
            messagebox.showerror("Erro", "Setor é obrigatório!")
            return

        if not status:
            messagebox.showerror("Erro", "Status é obrigatório!")
            return

        if not sond_id_raw.isdigit():
            messagebox.showerror("Erro", "SOND ID deve ser um número válido!")
            return

        if not periodicidade_raw.isdigit():
            messagebox.showerror("Erro", "Periodicidade deve ser um número válido!")
            return

        if not data_aquisicao_br:
            messagebox.showerror("Erro", "Data de aquisição é obrigatória!")
            return

        def parse_data(data_str):
            for formato in ("%d-%m-%Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(data_str, formato).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return None

        data_aquisicao = parse_data(data_aquisicao_br)
        if not data_aquisicao:
            messagebox.showerror("Erro", "Data de aquisição inválida! Use o formato DD-MM-YYYY ou DD/MM/YYYY.")
            return

        ultima_calibracao = None
        if ultima_calibracao_br:
            ultima_calibracao = parse_data(ultima_calibracao_br)
            if not ultima_calibracao:
                messagebox.showerror("Erro", "Última calibração inválida! Use o formato DD-MM-YYYY ou DD/MM/YYYY.")
                return

        confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente criar este equipamento?")
        if not confirmacao:
            return

        sigla = nome.split("-")[0].strip()
        sond_id = int(sond_id_raw)
        periodicidade = int(periodicidade_raw)

        equipamento_data = {
            "nome_eq": nome,
            "tipo_eq_id": tipos_eq.index(tipo) + 1,
            "sigla_eq": sigla,
            "setor_id": next((s[0] for s in tipos_setor if s[1] == setor), None),
            "status_id": next((s[0] for s in tipos_status if s[1] == status), None),
            "sond_id": sond_id,
            "data_aquisicao": data_aquisicao,
            "ultima_calibracao": ultima_calibracao,
            "periodicidade": periodicidade,
            "status_calibracao_id": next((s[0] for s in tipos_status_calibr if s[1] == self.combo_status_calibr.get()), None),
            "fabricante": self.entry_fabricante.get().strip(),
            "modelo": self.entry_modelo.get().strip(),
            "modelo_tecnico": self.entry_modelo_tecnico.get().strip(),
            "numero_serie": self.entry_num_serie.get().strip(),
            "extra_info": self.text_extra_info.get("1.0", "end").strip()
        }

        try:
            criar_equipamento(equipamento_data)
            messagebox.showinfo("Sucesso", "Equipamento criado com sucesso!")
            log_msg(f"Equipamento Criado: '{nome}'")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar equipamento:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = TelaCriacaoEquipamento(root)
    app.mainloop()
