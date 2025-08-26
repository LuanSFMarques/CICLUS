import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from controllers.equipamento_controller import criar_equipamento
from data.tipos import tipos_setor, tipos_status, tipos_status_calibr
from helpers import log_msg, get_connection, DB_FILE


class TelaCriacaoEquipamento(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Criar Novo Equipamento")
        self.geometry("1200x560")
        self.resizable(False, False)
        self.configure(bg="#F5F1E9")
        self.carregar_tipos_equipamento()
        self.criar_widgets()

    def carregar_tipos_equipamento(self):
        conn = get_connection(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM tipos_equipamento ORDER BY nome COLLATE NOCASE")
        self.tipos_equipamento = cursor.fetchall()
        conn.close()

    def criar_widgets(self):
        fonte_label = ("Courier New", 11, "bold")
        fonte_entry = ("Courier New", 11)

        def criar_label(parent, text, row, column):
            tk.Label(parent, text=text, bg="#F2EEE6", fg="#333333", font=fonte_label)\
                .grid(row=row, column=column, sticky="w", padx=5, pady=5)

        def criar_entry(parent, atributo, row, column, width=30):
            entry = tk.Entry(parent, width=width, font=fonte_entry)
            entry.grid(row=row, column=column, padx=5, pady=5, sticky="w")
            setattr(self, atributo, entry)

        def criar_combo(parent, atributo, values, row, column):
            combo = ttk.Combobox(parent, values=values, state="readonly", font=fonte_entry, width=28)
            combo.grid(row=row, column=column, padx=5, pady=5, sticky="w")
            combo.bind("<MouseWheel>", lambda e: "break")
            combo.bind("<Button-4>", lambda e: "break")
            combo.bind("<Button-5>", lambda e: "break")
            setattr(self, atributo, combo)

        def criar_text(parent, atributo, row, column, width=70, height=4):
            text = tk.Text(parent, width=width, height=height, font=fonte_entry, wrap="word")
            text.grid(row=row, column=column, padx=5, pady=5, columnspan=2, sticky="w")
            setattr(self, atributo, text)

                # Título acima do container
        titulo_label = tk.Label(
            self,
            text="Cadastro de Equipamento",
            bg="#F5F1E9",
            fg="#2F4F4F",
            font=("Courier New", 16, "bold")
        )
        titulo_label.pack(pady=(15, 0))


        # Container principal com borda e fundo escurecido
        container_frame = tk.Frame(self, bg="#F2EEE6", relief="sunken", bd=2)
        container_frame.pack(padx=20, pady=20, fill="both", expand=False)

        # Frame do formulário dentro do container
        form_frame = tk.Frame(container_frame, bg="#F2EEE6")
        form_frame.pack(padx=20, pady=20)

        # COLUNA 1
        criar_label(form_frame, "Nome do Equipamento:", 0, 0)
        criar_entry(form_frame, "entry_nome", 0, 1)

        criar_label(form_frame, "Tipo do Equipamento:", 1, 0)
        criar_combo(form_frame, "combo_tipo", [nome for _, nome in self.tipos_equipamento], 1, 1)

        criar_label(form_frame, "Setor:", 2, 0)
        criar_combo(form_frame, "combo_setor", sorted([s[1] for s in tipos_setor]), 2, 1)

        criar_label(form_frame, "Status:", 3, 0)
        criar_combo(form_frame, "combo_status", sorted([s[1] for s in tipos_status]), 3, 1)

        criar_label(form_frame, "SOND ID (Número único):", 4, 0)
        criar_entry(form_frame, "entry_sond", 4, 1, width=20)

        criar_label(form_frame, "Data de Aquisição (DD-MM-YYYY):", 5, 0)
        criar_entry(form_frame, "entry_data_aq", 5, 1, width=20)

        criar_label(form_frame, "Última Calibração (DD-MM-YYYY):", 6, 0)
        criar_entry(form_frame, "entry_ultima_cal", 6, 1, width=20)

        criar_label(form_frame, "Periodicidade (meses):", 7, 0)
        criar_entry(form_frame, "entry_periodicidade", 7, 1, width=10)

        criar_label(form_frame, "Status de Calibração:", 8, 0)
        criar_combo(form_frame, "combo_status_calibr", sorted([s[1] for s in tipos_status_calibr]), 8, 1)

        # COLUNA 2
        criar_label(form_frame, "Fabricante:", 0, 2)
        criar_entry(form_frame, "entry_fabricante", 0, 3)

        criar_label(form_frame, "Modelo:", 1, 2)
        criar_entry(form_frame, "entry_modelo", 1, 3)

        criar_label(form_frame, "Modelo Técnico:", 2, 2)
        criar_entry(form_frame, "entry_modelo_tecnico", 2, 3)

        criar_label(form_frame, "Número de Série:", 3, 2)
        criar_entry(form_frame, "entry_num_serie", 3, 3)

        criar_label(form_frame, "Informações Extras:", 4, 2)
        criar_text(form_frame, "text_extra_info", 5, 2)

        # Frame de botões
        btn_frame = tk.Frame(self, bg="#F5F1E9")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="SALVAR", command=self.salvar_equipamento,
            bg="#C85A17", fg="white", font=("Courier New", 12, "bold"),
            width=14, height=2, activebackground="#E38B2B"
        ).pack(side="left", padx=40)

        tk.Button(
            btn_frame, text="CANCELAR", command=self.destroy,
            bg="#8B8B8B", fg="white", font=("Courier New", 12, "bold"),
            width=14, height=2, activebackground="#A9A9A9"
        ).pack(side="left", padx=40)



    def salvar_equipamento(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get().strip()
        setor = self.combo_setor.get().strip()
        status = self.combo_status.get().strip()
        sond_id_raw = self.entry_sond.get().strip()
        data_aquisicao_br = self.entry_data_aq.get().strip()
        ultima_calibracao_br = self.entry_ultima_cal.get().strip()
        periodicidade_raw = self.entry_periodicidade.get().strip()

        if not nome or "-" not in nome:
            messagebox.showerror("Erro", "Informe um nome válido (com '-').")
            return
        if not sond_id_raw.isdigit():
            messagebox.showerror("Erro", "SOND ID deve ser um número válido!")
            return
        if not periodicidade_raw.isdigit():
            messagebox.showerror("Erro", "Periodicidade deve ser um número válido!")
            return

        def parse_data(data_str):
            for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(data_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return None

        data_aquisicao = parse_data(data_aquisicao_br) if data_aquisicao_br else None
        ultima_calibracao = parse_data(ultima_calibracao_br) if ultima_calibracao_br else None

        if data_aquisicao_br and not data_aquisicao:
            messagebox.showerror("Erro", "Data de aquisição inválida!")
            return
        if ultima_calibracao_br and not ultima_calibracao:
            messagebox.showerror("Erro", "Data de calibração inválida!")
            return

        confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente criar este equipamento?")
        if not confirmacao:
            return

        sigla = nome.split("-")[0].strip()
        sond_id = int(sond_id_raw)
        periodicidade = int(periodicidade_raw)

        equipamento_data = {
            "nome_eq": nome,
            "tipo_eq_id": next((id_ for id_, nome_ in self.tipos_equipamento if nome_ == tipo), None),
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
