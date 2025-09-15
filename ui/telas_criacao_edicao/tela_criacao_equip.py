import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

from controllers.equipamento_controller import criar_equipamento
from data.tipos import tipos_setor, tipos_status, tipos_status_calibr
from helpers import log_msg, get_connection, DB_FILE


class TelaCriacaoEquipamento(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Criar Novo Equipamento")
        self.geometry("1200x560")
        self.resizable(False, False)
        self.configure(bg="#F5F1E9")
        self.carregar_tipos_equipamento()
        self.criar_widgets()

        if master is not None:
            pos_x = master.winfo_x() + 50
            pos_y = master.winfo_y() + 50
            self.geometry(f"{1200}x{560}+{pos_x}+{pos_y}")
        else:
            self.geometry(f"{1200}x{560}")

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
            # evitar scroll acidental
            combo.bind("<MouseWheel>", lambda e: "break")
            combo.bind("<Button-4>", lambda e: "break")
            combo.bind("<Button-5>", lambda e: "break")
            setattr(self, atributo, combo)

        def criar_text(parent, atributo, row, column, width=50, height=6):
            text = tk.Text(parent, width=width, height=height, font=fonte_entry, wrap="word", bd=2)
            text.grid(row=row, column=column, padx=5, pady=5, columnspan=2, sticky="w")
            setattr(self, atributo, text)

        # Título
        tk.Label(
            self,
            text="Cadastro de Equipamento",
            bg="#F5F1E9",
            fg="#2F4F4F",
            font=("Courier New", 16, "bold")
        ).pack(pady=(15, 0))

        # Container
        container_frame = tk.Frame(self, bg="#F2EEE6", relief="sunken", bd=2)
        container_frame.pack(padx=20, pady=20, fill="both", expand=False)

        # Formulário
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

        criar_label(form_frame, "Data de Aquisição (DD-MM-YYYY ou DD/MM/YYYY):", 5, 0)
        criar_entry(form_frame, "entry_data_aq", 5, 1, width=20)

        criar_label(form_frame, "Última Calibração (DD-MM-YYYY ou DD/MM/YYYY):", 6, 0)
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

        # Botões
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

    # ---------- Utilidades de validação ----------
    @staticmethod
    def _parse_data_br(data_str: str):
        """Retorna string no formato ISO '%Y-%m-%d' se válido, senão None."""
        if not data_str:
            return None
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
        Exemplos válidos: PEN-001, ABC-12-XYZ
        Exemplos inválidos: P3N-001, 123-ABC
        """
        return bool(re.fullmatch(r"[A-Za-z]+-.+", nome))

    @staticmethod
    def _fabricante_letras_len_ok(fab: str, limite: int = 20) -> bool:
        """Conta apenas letras (A-Z/a-z); não permite mais que 'limite' letras."""
        somente_letras = re.sub(r"[^A-Za-z]", "", fab or "")
        return len(somente_letras) <= limite

    @staticmethod
    def _capitalize_fabricante(fab: str) -> str:
        """
        Tratamento: cada palavra com primeira letra maiúscula e o resto minúsculo.
        SoloTest -> Solotest; teste 123 -> Teste 123; oi oi -> Oi Oi
        """
        return (fab or "").strip().title()

    # ---------- Fluxo principal ----------
    def salvar_equipamento(self):
        # Coleta bruta (sem transformar ainda)
        nome = self.entry_nome.get().strip().upper()
        tipo = self.combo_tipo.get().strip()
        setor = self.combo_setor.get().strip()
        status = self.combo_status.get().strip()
        sond_id_raw = self.entry_sond.get().strip()
        data_aquisicao_br = self.entry_data_aq.get().strip()
        ultima_calibracao_br = self.entry_ultima_cal.get().strip()
        periodicidade_raw = self.entry_periodicidade.get().strip()
        fabricante_raw = self.entry_fabricante.get().strip()
        modelo = self.entry_modelo.get().strip()
        modelo_tecnico = self.entry_modelo_tecnico.get().strip()
        numero_serie = self.entry_num_serie.get().strip()
        extra_info = self.text_extra_info.get("1.0", "end").strip()
        status_calibracao = self.combo_status_calibr.get().strip()

        # ---- Validações exigidas ----

        # Nome do equipamento: padrão exato "SIGLA-NUMERO"
        if not nome or not self._regex_nome_ok(nome):
            messagebox.showerror(
                "Nome de Equipamento Inválido",
                (
                    "O nome do equipamento é inválido.\n\n"
                    "Condições para um nome válido:\n"
                    "• Deve conter exatamente 1 hífen '-'.\n"
                    "• Antes do hífen: apenas letras (sem números).\n"
                    "• Depois do hífen: apenas números (sem letras).\n"
                    "Exemplos válidos: PEN-001, ABC-12, X-9"
                )
            )
            return

        # Obrigatoriedade dos combos (não aceitar vazio/nulo)
        if not tipo:
            messagebox.showerror("Erro", "Selecione um Tipo do Equipamento (não pode ficar vazio).")
            return
        if not setor:
            messagebox.showerror("Erro", "Selecione um Setor (não pode ficar vazio).")
            return
        if not status:
            messagebox.showerror("Erro", "Selecione um Status (não pode ficar vazio).")
            return
        if not status_calibracao:
            messagebox.showerror("Erro", "Selecione um Status de Calibração (não pode ficar vazio).")
            return

        # SOND ID inteiro
        if not sond_id_raw.isdigit():
            messagebox.showerror("Erro", "SOND ID deve ser um número inteiro válido.")
            return

        # Periodicidade em meses: inteiro
        if not periodicidade_raw.isdigit():
            messagebox.showerror("Erro", "Periodicidade (meses) deve ser um número inteiro.")
            return

        # Datas: formatos aceitos e relação entre datas
        data_aquisicao_iso = self._parse_data_br(data_aquisicao_br) if data_aquisicao_br else None
        if data_aquisicao_br and not data_aquisicao_iso:
            messagebox.showerror(
                "Data de Aquisição Inválida",
                "Formato inválido. Use: DD-MM-YYYY ou DD/MM/YYYY."
            )
            return

        ultima_calibracao_iso = self._parse_data_br(ultima_calibracao_br) if ultima_calibracao_br else None
        if ultima_calibracao_br and not ultima_calibracao_iso:
            messagebox.showerror(
                "Data de Última Calibração Inválida",
                "Formato inválido. Use: DD-MM-YYYY ou DD/MM/YYYY."
            )
            return

        # Regra: última calibração deve ser >= data de aquisição (se ambas existirem)
        if data_aquisicao_iso and ultima_calibracao_iso:
            try:
                dt_aq = datetime.strptime(data_aquisicao_iso, "%Y-%m-%d")
                dt_uc = datetime.strptime(ultima_calibracao_iso, "%Y-%m-%d")
                if dt_uc < dt_aq:
                    messagebox.showerror(
                        "Inconsistência de Datas",
                        "A data de última calibração deve ser no mínimo igual à data de aquisição."
                    )
                    return
            except Exception:
                # segurança (não deve ocorrer pois já validamos)
                messagebox.showerror("Erro", "Falha ao validar as datas fornecidas.")
                return

        # Fabricante: não permitir mais que 20 letras (contando só letras A-Z)
        if fabricante_raw and not self._fabricante_letras_len_ok(fabricante_raw, limite=20):
            messagebox.showerror(
                "Fabricante Inválido",
                "O nome do fabricante não pode conter mais que 20 letras (A-Z)."
            )
            return

        # Confirmação antes dos TRATAMENTOS
        confirmacao = messagebox.askyesno("Confirmação", "Deseja realmente criar este equipamento?")
        if not confirmacao:
            return

        # ---- TRATAMENTOS (aplicados somente após confirmação) ----

        # Capitalize do fabricante (MARTES->Martes; SoloTest->Solotest; teste->Teste)
        fabricante_tratado = self._capitalize_fabricante(fabricante_raw)

        # Revalidar o limite de letras após tratamento (por segurança)
        if fabricante_tratado and not self._fabricante_letras_len_ok(fabricante_tratado, limite=20):
            messagebox.showerror(
                "Fabricante Inválido",
                "O nome do fabricante não pode conter mais que 20 letras (A-Z)."
            )
            return

        # Conversões finais
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
            "data_aquisicao": data_aquisicao_iso,          # ISO YYYY-MM-DD ou None
            "ultima_calibracao": ultima_calibracao_iso,    # ISO YYYY-MM-DD ou None
            "periodicidade": periodicidade,
            "status_calibracao_id": next((s[0] for s in tipos_status_calibr if s[1] == status_calibracao), None),
            "fabricante": fabricante_tratado,
            "modelo": modelo,
            "modelo_tecnico": modelo_tecnico,
            "numero_serie": numero_serie,
            "extra_info": extra_info
        }

        try:
            criar_equipamento(equipamento_data)
            messagebox.showinfo("Sucesso", "Equipamento criado com sucesso!")
            log_msg(f"Equipamento Criado: '{nome}'")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar equipamento:\n{e}")
