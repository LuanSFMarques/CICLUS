import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re  # <-- necessário para regex

from controllers.equipamento_controller import obter_equipamento_cru, atualizar_equipamento
from data.tipos import tipos_setor, tipos_status, tipos_status_calibr
from helpers import log_msg, get_connection, DB_FILE


class TelaEdicaoEquipamento(tk.Toplevel):
    def __init__(self, equip_id, master):
        super().__init__(master)
        self.title(f"Editar Equipamento - ID {equip_id}")
        self.geometry("1200x560")
        self.resizable(False, False)
        self.configure(bg="#F5F1E9")

        if master is not None:
            pos_x = master.winfo_x() + 50
            pos_y = master.winfo_y() + 50
            self.geometry(f"{1200}x{560}+{pos_x}+{pos_y}")
        else:
            self.geometry(f"{1200}x{560}")

        self.equip_id = equip_id
        self.equipamento = obter_equipamento_cru(equip_id)
        if not self.equipamento:
            messagebox.showerror("Erro", "Equipamento não encontrado.")
            self.destroy()
            return

        self.carregar_tipos_equipamento()
        self.criar_widgets()
        self.preencher_campos()

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
            combo.bind("<Button-4>", lambda e: "break")  # Linux
            combo.bind("<Button-5>", lambda e: "break")  # Linux
            setattr(self, atributo, combo)

        def criar_text(parent, atributo, row, column, width=50, height=6):
            text = tk.Text(parent, width=width, height=height, font=fonte_entry, wrap="word", bd=2)
            text.grid(row=row, column=column, padx=5, pady=5, columnspan=2, sticky="w")
            setattr(self, atributo, text)

        tk.Label(
            self,
            text="Edição de Equipamento",
            bg="#F5F1E9",
            fg="#2F4F4F",
            font=("Courier New", 16, "bold")
        ).pack(pady=(15, 0))

        container_frame = tk.Frame(self, bg="#F2EEE6", relief="sunken", bd=2)
        container_frame.pack(padx=20, pady=20, fill="both", expand=False)

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

        criar_label(form_frame, "Data de Aquisição (DD-MM-YYYY):", 4, 0)
        criar_entry(form_frame, "entry_data_aq", 4, 1, width=20)

        criar_label(form_frame, "Última Calibração (DD-MM-YYYY):", 5, 0)
        criar_entry(form_frame, "entry_ultima_cal", 5, 1, width=20)

        criar_label(form_frame, "Periodicidade (meses):", 6, 0)
        criar_entry(form_frame, "entry_periodicidade", 6, 1, width=10)

        criar_label(form_frame, "Status de Calibração:", 7, 0)
        criar_combo(form_frame, "combo_status_calibr", sorted([s[1] for s in tipos_status_calibr]), 7, 1)

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

        btn_frame = tk.Frame(self, bg="#F5F1E9")
        btn_frame.pack(pady=10)

        btn_width = 15
        btn_height = 1

        tk.Button(
            btn_frame, text="SALVAR", command=self.salvar_equipamento,
            bg="#C85A17", fg="white", font=("Courier New", 12, "bold"),
            width=btn_width, height=btn_height, activebackground="#E38B2B"
        ).pack(side="left", padx=40)

        tk.Button(
            btn_frame, text="CANCELAR", command=self.destroy,
            bg="#8B8B8B", fg="white", font=("Courier New", 12, "bold"),
            width=btn_width, height=btn_height, activebackground="#A9A9A9"
        ).pack(side="left", padx=40)

    def preencher_campos(self):
        e = self.equipamento

        def get_nome_por_id(lista, id_):
            return next((nome for ident, nome in lista if ident == id_), "")

        self.entry_nome.insert(0, e["nome_eq"])
        self.combo_tipo.set(get_nome_por_id(self.tipos_equipamento, e["tipo_eq_id"]))
        self.combo_setor.set(get_nome_por_id(tipos_setor, e["setor_id"]))
        self.combo_status.set(get_nome_por_id(tipos_status, e["status_id"]))
        self.entry_data_aq.insert(0, self.formatar_data(e["data_aquisicao"]))
        self.entry_ultima_cal.insert(0, self.formatar_data(e["ultima_calibracao"]))
        self.entry_periodicidade.insert(0, str(e["periodicidade"]))
        self.combo_status_calibr.set(get_nome_por_id(tipos_status_calibr, e["status_calibracao_id"]))
        self.entry_fabricante.insert(0, e["fabricante"])
        self.entry_modelo.insert(0, e["modelo"])
        self.entry_modelo_tecnico.insert(0, e["modelo_tecnico"])
        self.entry_num_serie.insert(0, str(e.get("numero_serie", "")))
        self.text_extra_info.insert("1.0", e["extra_info"])

    def formatar_data(self, data_str):
        if not data_str:
            return ""
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d-%m-%Y")

    def converter_data(self, data_str):
        for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(data_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    @staticmethod
    def _regex_nome_ok(nome: str) -> bool:
        """
        Regras:
        - Deve conter pelo menos 1 hífen '-'
        - Parte antes do primeiro hífen: apenas letras (A-Z/a-z), sem números
        - Parte após o primeiro hífen: pode conter números, letras ou hífens
        """
        return bool(re.fullmatch(r"[A-Za-z]+-.+", nome))

    def salvar_equipamento(self):
        try:
            nome = self.entry_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "O campo 'Nome do Equipamento' é obrigatório.")
                return

            if not self._regex_nome_ok(nome):
                messagebox.showerror(
                    "Erro",
                    "Nome inválido.\n\nRegras:\n"
                    "- Deve conter pelo menos 1 hífen '-'\n"
                    "- Primeira parte só pode conter letras (sem números)\n"
                    "- Após o hífen pode haver letras, números ou outros hífens"
                )
                return

            data_aq_raw = self.entry_data_aq.get().strip()
            ultima_cal_raw = self.entry_ultima_cal.get().strip()

            data_aq = self.converter_data(data_aq_raw) if data_aq_raw else None
            ultima_cal = self.converter_data(ultima_cal_raw) if ultima_cal_raw else None

            if data_aq_raw and not data_aq:
                messagebox.showerror("Erro", "Data de Aquisição inválida. Use DD-MM-YYYY.")
                return
            if ultima_cal_raw and not ultima_cal:
                messagebox.showerror("Erro", "Data de Última Calibração inválida. Use DD-MM-YYYY.")
                return

            periodicidade_raw = self.entry_periodicidade.get().strip()
            if periodicidade_raw and not periodicidade_raw.isdigit():
                messagebox.showerror("Erro", "Periodicidade deve ser um número inteiro.")
                return
            periodicidade = int(periodicidade_raw) if periodicidade_raw else None

            sigla = nome.split("-")[0]

            tipo_nome = self.combo_tipo.get()
            tipo_id = next((id_ for id_, nome in self.tipos_equipamento if nome == tipo_nome), None)

            novos_dados = {
                "nome_eq": nome,
                "tipo_eq_id": tipo_id,
                "sigla_eq": sigla,
                "setor_id": next((i for i, nome in tipos_setor if nome == self.combo_setor.get()), None),
                "status_id": next((i for i, nome in tipos_status if nome == self.combo_status.get()), None),
                "data_aquisicao": data_aq,
                "ultima_calibracao": ultima_cal,
                "periodicidade": periodicidade,
                "status_calibracao_id": next((i for i, nome in tipos_status_calibr if nome == self.combo_status_calibr.get()), None),
                "fabricante": self.entry_fabricante.get().strip(),
                "modelo": self.entry_modelo.get().strip(),
                "modelo_tecnico": self.entry_modelo_tecnico.get().strip(),
                "numero_serie": self.entry_num_serie.get().strip(),
                "extra_info": self.text_extra_info.get("1.0", "end").strip()
            }

            confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente salvar as alterações?")
            if not confirmacao:
                return

            atualizar_equipamento(self.equip_id, novos_dados)
            messagebox.showinfo("Sucesso", "Equipamento atualizado com sucesso!")
            log_msg(f"Equipamento Editado: '{nome}'")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
