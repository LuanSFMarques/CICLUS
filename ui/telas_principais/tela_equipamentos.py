import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import unicodedata
import re
import webbrowser
from pathlib import Path

from controllers.equipamento_controller import listar_equipamentos_resumido, excluir_equipamento
from ui.telas_criacao_edicao.tela_criacao_equip import TelaCriacaoEquipamento
from ui.telas_criacao_edicao.tela_edicao_equip import TelaEdicaoEquipamento
from ui.telas_principais.tela_itens import TelaCicloVida
from ui.telas_misc.tela_plano_calibr import TelaPlanoDeCalibracao
from data.atualizar_calibracao import atualizar_status_calibr_todos
from helpers import DB_FILE

CAMINHO_LOGO_SUPORTE = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "suporte_logo_laranja.png"
CAMINHO_LOGO_CICLUS = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "ciclus_logo_laranja.png"

STATUS_COR = {
    "ATIVO": "#A8D5BA",
    "INATIVO": "#F4B6B6",
    "INCERTO": "#D3D3D3"
}

CALIB_COR = {
    "C": "#DFF2BB",
    "NC": "#FFB3B3",
    "E": "#B9D6FF",
    "I": "#D6D6D6"
}

ITENS_POR_PAGINA = 20

class TelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        try:
            self.logo_icon = tk.PhotoImage(file="assets/logos/teste.png")
            self.iconphoto(True, self.logo_icon)
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

        self.title("Ciclus - Lista de Equipamentos")
        self.geometry("1200x700")
        self.configure(bg="#F5F1E9")
        self.resizable(False, False)

        self.dados_originais = listar_equipamentos_resumido()
        self.dados_processados = self.preprocessar_dados(self.dados_originais)
        self.pagina_atual = 1
        self.resultados_filtrados = self.dados_processados

        self.criar_widgets()
        self.exibir_pagina(1)

    def normalizar(self, texto):
        texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
        texto = re.sub(r"[^\w\s-]", "", texto)
        return texto.lower().strip()

    def preprocessar_dados(self, dados):
        processados = []
        for item in dados:
            nome = item.get("nome_eq", "None").lower()
            sigla = nome.split("-")[0].strip() if "-" in nome else "None"
            setor = item.get("setor", "None").lower()
            status = item.get("status", "None").lower()
            status_calibr = item.get("status_calibr", "None").lower()
            tipo = item.get("tipo", "None").lower()
            modelo = item.get("modelo", "None")

            processados.append({
                **item,
                "sigla": sigla,
                "nome_lower": nome,
                "tipo_lower": tipo,
                "modelo": modelo,
                "setor_lower": setor,
                "status_lower": status,
                "status_calibr_lower": status_calibr,
            })
        return processados

    def criar_widgets(self):
        try:
            imagem_logo_topo = Image.open(CAMINHO_LOGO_CICLUS).convert("RGBA")  # Garante transparência
            imagem_logo_topo = imagem_logo_topo.resize((200, 50), Image.Resampling.LANCZOS)
            self.logo_topo = ImageTk.PhotoImage(imagem_logo_topo)
            tk.Label(self, image=self.logo_topo, bg="#F5F1E9", relief="raised", bd=3).pack(pady=(20, 5))  # Define o mesmo bg do fundo

        except Exception as e:
            print(f"Erro ao carregar logo no topo: {e}")


        tk.Label(self, text="Lista de Equipamentos", font=("Courier New", 18, "bold"),
                 bg="#EEE6D9", fg="#333333", relief="raised", bd=3,
                 padx=10, pady=4).pack(pady=(10, 5))

        tk.Button(self, text="Documentação", font=("Lucida Console", 10, "bold"),
          bg="#E6A47B", fg="#EEE6D9", relief="raised", bd=3,
          padx=44, pady=2, activebackground="#DDD0C8",
          activeforeground="#5C4033", command=self.abrir_documentacao
        ).place(relx=1.0, x=-15, y=19, anchor="ne")

        tk.Button(self, text="Sond", font=("Lucida Console", 10, "bold"),
                bg="#E6A47B", fg="#EEE6D9", relief="raised", bd=3,
                padx=80, pady=2, activebackground="#DDD0C8",
                activeforeground="#5C4033", command=self.abrir_sond
        ).place(relx=1.0, x=-15, y=59, anchor="ne")

        tk.Button(self, text="Gráficos", font=("Lucida Console", 10, "bold", "overstrike"),
                bg="#3B3B3B", fg="#EEE6D9", relief="raised", bd=3,
                padx=62, pady=2, activebackground="#DDD0C8",
                activeforeground="#5C4033", command=self.abrir_graficos
        ).place(relx=1.0, x=-15, y=99, anchor="ne")

        tk.Button(self, text="Plano de Calibr.", font=("Lucida Console", 10, "bold"),
                bg="#E6A47B", fg="#EEE6D9", relief="raised", bd=3,
                padx=26, pady=2, activebackground="#DDD0C8",
                activeforeground="#5C4033", command=self.abrir_plano_calibr
        ).place(relx=1.0, x=-15, y=139, anchor="ne")

        tk.Button(self, text="Atualizar", font=("Lucida Console", 10, "bold"),
          bg="#E6A47B", fg="#EEE6D9", relief="raised", bd=3,
          padx=44, pady=2, activebackground="#DDD0C8",
          activeforeground="#5C4033", command=self.atualizar_status_e_recarregar
        ).place(relx=1.0, x=-1005, y=658, anchor="ne")

        self.var_busca = tk.StringVar()
        entry_busca = tk.Entry(self, textvariable=self.var_busca, font=("Lucida Console", 12),
                               width=50, bg="#FDFCF8", fg="#333333", relief="sunken", bd=3,
                               insertbackground="#333333")
        entry_busca.pack(pady=5)
        entry_busca.bind("<KeyRelease>", self.filtrar_lista)

        container = tk.Frame(self, bg="#F5F1E9", bd=3, relief="groove")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(container, bg="#F5F1E9", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.lista_frame = tk.Frame(self.canvas, bg="#F5F1E9")

        self.lista_frame.bind("<Configure>", self.atualizar_scrollregion)
        self.canvas.create_window((0, 0), window=self.lista_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        container.bind("<Enter>", self._bind_to_mousewheel)
        container.bind("<Leave>", self._unbind_from_mousewheel)

        self.paginacao_frame = tk.Frame(self, bg="#F5F1E9")
        self.paginacao_frame.pack(pady=10)

        tk.Button(self, text="Criar novo equipamento", bg="#C85A17", fg="#EEE6D9",
                  font=("Lucida Console", 12, "bold"), relief="raised", bd=4,
                  activebackground="#E38B2B", activeforeground="white",
                  command=self.abrir_criacao).pack(pady=15)
        try:
            imagem_original = Image.open(CAMINHO_LOGO_SUPORTE).convert("RGBA")
            imagem_redimensionada = imagem_original.resize((140, 30), Image.Resampling.LANCZOS)
            self.logo_suporte = ImageTk.PhotoImage(imagem_redimensionada)
            logo_label = tk.Label(self, image=self.logo_suporte, bg="#F5F1E9")
            logo_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        except Exception as e:
            print(f"Erro ao carregar logo de suporte: {e}")

    def adicionar_item(self, item):
        bg_status = STATUS_COR.get(item.get("status", "INCERTO").strip().upper(), "#CCCCCC")

        STATUS_CALIB_MAP = {
            "calibrado": "C",
            "não_calibrado": "NC",
            "especial": "E",
            "incerto": "I"
        }

        status_calibr_text = item.get("status_calibr", "incerto").strip().lower()
        status_calibr_key = STATUS_CALIB_MAP.get(status_calibr_text, "I")
        bg_calibr = CALIB_COR.get(status_calibr_key, "#DDDDDD")

        container_item = tk.Frame(self.lista_frame, bg="#F0F0F0", bd=1, relief="ridge", padx=5, pady=5)
        container_item.pack(fill="x", pady=6, padx=3)
        container_item.columnconfigure(1, weight=1)

        quadrado_frame = tk.Frame(container_item, bg=bg_status, width=22, height=22,
                          relief="raised", bd=2)
        quadrado_frame.grid(row=0, column=0, padx=(0, 10), pady=5)
        quadrado_frame.grid_propagate(False)

        frame_info = tk.Frame(container_item, bg=bg_calibr, bd=1, relief="sunken")
        frame_info.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        frame_conteudo = tk.Frame(frame_info, bg=bg_calibr, padx=12, pady=12)
        frame_conteudo.pack(fill="x", expand=True)

        info_text = f"{item['nome_eq']} / {item['tipo']} ({item['modelo']}) / {item['setor']} / {item['status']} / {item['status_calibr']}"
        lbl_info = tk.Label(frame_conteudo, text=info_text, bg=bg_calibr, anchor="w",
                            font=("Lucida Console", 12), wraplength=700, fg="#222222")
        lbl_info.pack(side="left", fill="x", expand=True)

        frame_lateral = tk.Frame(container_item, bg="white", bd=1, relief="sunken")
        frame_lateral.grid(row=0, column=2, sticky="ns")

        tk.Label(frame_lateral, text=f"IDS: {item['ids']}", bg="white",
                 font=("Lucida Console", 12, "bold"), width=12,
                 anchor="center", fg="#000000").pack(side="left", padx=5, pady=10)

        tk.Button(frame_lateral, text="Editar", font=("Lucida Console", 10, "bold"),
                  bg="#C85A17", fg="white", bd=2, relief="raised",
                  activebackground="#C85A17", activeforeground="white",
                  command=lambda eq=item: self.abrir_edicao(eq)).pack(side="left", padx=5, pady=10)

        tk.Button(frame_lateral, text="X", font=("Lucida Console", 12, "bold"),
                  bg="#F44336", fg="white", bd=2, relief="raised",
                  activebackground="#C62828", activeforeground="white",
                  width=2, command=lambda eq=item: self.confirmar_exclusao(eq)).pack(side="left", padx=5, pady=10)

        def abrir_ciclo_vida_se_nao_editar(event):
            if event.widget != frame_lateral:
                self.abrir_tela_itens(item)

        for widget in [container_item, frame_info, quadrado_frame, frame_conteudo, lbl_info, frame_lateral]:
            widget.bind("<Button-1>", abrir_ciclo_vida_se_nao_editar)

    def filtrar_lista(self, event=None):
        busca = self.normalizar(self.var_busca.get())
        termos = busca.split()

        if not termos:
            self.resultados_filtrados = self.dados_processados
        else:
            resultados = []
            for item in self.dados_processados:
                campos = [
                    self.normalizar(item["sigla"]),
                    self.normalizar(item["nome_eq"]),
                    self.normalizar(item["modelo"]),
                    self.normalizar(item["setor_lower"]),
                    self.normalizar(item["tipo_lower"]),
                    self.normalizar(item["status_lower"]),
                    self.normalizar(item["status_calibr_lower"])
                ]
                if all(re.search(rf"\b{re.escape(termo)}\b", " ".join(campos), re.IGNORECASE) for termo in termos):
                    resultados.append(item)

            self.resultados_filtrados = resultados

        self.pagina_atual = 1
        self.exibir_pagina(self.pagina_atual)

    def exibir_pagina(self, numero_pagina):
        self.pagina_atual = numero_pagina
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        start = (numero_pagina - 1) * ITENS_POR_PAGINA
        end = start + ITENS_POR_PAGINA
        page_items = sorted(self.resultados_filtrados, key=lambda x: x.get("ids", 0))[start:end]

        for item in page_items:
            self.adicionar_item(item)

        self.atualizar_paginacao()

    def atualizar_paginacao(self):
        for widget in self.paginacao_frame.winfo_children():
            widget.destroy()

        total_itens = len(self.resultados_filtrados)
        total_paginas = max(1, (total_itens + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)

        max_botoes = 20
        inicio = max(1, self.pagina_atual - max_botoes // 2)
        fim = min(total_paginas, inicio + max_botoes - 1)
        if fim - inicio < max_botoes:
            inicio = max(1, fim - max_botoes + 1)

        for i in range(inicio, fim + 1):
            tk.Button(
                self.paginacao_frame, text=str(i), width=3,
                relief="sunken" if i == self.pagina_atual else "raised",
                bg="#C85A17" if i == self.pagina_atual else "SystemButtonFace",
                fg="white" if i == self.pagina_atual else "black",
                command=lambda p=i: self.exibir_pagina(p)
            ).pack(side="left", padx=2)

    def atualizar_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        direction = 1 if event.num == 5 or event.delta < 0 else -1
        self.canvas.yview_scroll(direction, "units")

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_from_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def abrir_criacao(self):
        criacao = TelaCriacaoEquipamento(self)
        criacao.grab_set()
        self.wait_window(criacao)
        self.dados_originais = listar_equipamentos_resumido()
        self.dados_processados = self.preprocessar_dados(self.dados_originais)
        self.filtrar_lista()

    def abrir_edicao(self, equipamento):
        edicao = TelaEdicaoEquipamento(equipamento["id"], master=self)
        edicao.grab_set()
        self.wait_window(edicao)
        self.dados_originais = listar_equipamentos_resumido()
        self.dados_processados = self.preprocessar_dados(self.dados_originais)
        self.filtrar_lista()

    def confirmar_exclusao(self, equipamento):
        if messagebox.askyesno("Confirmação", f"Excluir {equipamento['nome_eq']}?"):
            excluir_equipamento(equipamento["id"])
            self.dados_originais = listar_equipamentos_resumido()
            self.dados_processados = self.preprocessar_dados(self.dados_originais)
            self.filtrar_lista()

    def atualizar_status_e_recarregar(self):
        atualizar_status_calibr_todos(DB_FILE)
        self.dados_originais = listar_equipamentos_resumido()
        self.dados_processados = self.preprocessar_dados(self.dados_originais)
        self.filtrar_lista()


    def abrir_tela_itens(self, equipamento):
        janela = TelaCicloVida(self, equipamento)
        self.update_idletasks()
        janela.geometry(f"+{self.winfo_x()+50}+{self.winfo_y()+50}")
        janela.grab_set()

    def abrir_documentacao(self):
        webbrowser.open_new_tab("https://github.com/LuanSFMarques/CICLUS")

    def abrir_sond(self):
        webbrowser.open_new_tab("https://www.sond.com.br/ativos-laboratorio-lista/status/1/")

    def abrir_graficos(self):
        messagebox.showinfo("Gráficos", "Função de gráficos será implementada em breve.")

    def abrir_plano_calibr(self):
        TelaPlanoDeCalibracao()

if __name__ == "__main__":
    app = TelaPrincipal()
    app.mainloop()
