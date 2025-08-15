import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from datetime import datetime

from controllers.itens_controller import obter_equipamento_por_id, obter_itens_ciclo_vida_por_equipamento, excluir_item
from ui.telas_criacao_edicao.tela_criacao_ciclo import TelaCriacaoCiclo
from ui.telas_principais.tela_desc_item import TelaDescricaoItem
from ui.telas_criacao_edicao.tela_edicao_ciclo import TelaEdicaoCiclo

class TelaCicloVida(tk.Toplevel):
    def __init__(self, master, equipamento):
        super().__init__(master)
        self.title(f"Ciclo de Vida - {equipamento['nome_eq']}")
        self.configure(bg="#F5F1E9")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.equipamento = equipamento
        self.equip_id = equipamento["id"]

        # Título estilizado
        frame_titulo = tk.Frame(self, bg="#F5F1E9")
        frame_titulo.pack(pady=15)

        moldura = tk.Frame(frame_titulo, bg="#EEE6D9", bd=3, relief="raised")
        moldura.pack()

        titulo = tk.Label(
            moldura,
            text=f"Ciclo de Vida do Equipamento | {equipamento['nome_eq']}",
            font=("Courier New", 20, "bold"),
            bg="#EEE6D9",
            fg="#333333"
        )
        titulo.pack(padx=10, pady=5)

        # Container principal
        container = tk.Frame(self, bg="#F5F1E9")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        container.columnconfigure(0, weight=1, uniform="col")
        container.columnconfigure(1, weight=2, uniform="col") 
        container.rowconfigure(0, weight=1) 

        # Esquerda - Dados do equipamento com scroll
        self.frame_esquerdo_container = tk.Frame(container, bg="#EDE6D6", bd=1, relief="sunken")
        self.frame_esquerdo_container.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)

        self.canvas_esquerdo = tk.Canvas(self.frame_esquerdo_container, bg="#EDE6D6", highlightthickness=0)
        self.scrollbar_esquerdo = ttk.Scrollbar(self.frame_esquerdo_container, orient="vertical", command=self.canvas_esquerdo.yview)
        self.scroll_frame_esquerdo = tk.Frame(self.canvas_esquerdo, bg="#EDE6D6")

        self.scroll_frame_esquerdo.bind(
            "<Configure>",
            lambda e: self.canvas_esquerdo.configure(scrollregion=self.canvas_esquerdo.bbox("all"))
        )

        window_id_esquerdo = self.canvas_esquerdo.create_window((0, 0), window=self.scroll_frame_esquerdo, anchor="nw")

        def ajustar_largura_conteudo_esquerdo(event):
            self.canvas_esquerdo.itemconfig(window_id_esquerdo, width=event.width)

        self.canvas_esquerdo.bind("<Configure>", ajustar_largura_conteudo_esquerdo)
        self.canvas_esquerdo.configure(yscrollcommand=self.scrollbar_esquerdo.set)

        self.canvas_esquerdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_esquerdo.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_direito = tk.Frame(container, bg="#E3DDD2", bd=1, relief="sunken")
        self.frame_direito.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=10)

        btn_adicionar_item = tk.Button(
            self,
            text="Adicionar Item ao Ciclo de Vida",
            bg="#C85A17",
            fg="#E3DDD2",
            font=("Lucida Console", 12, "bold"),
            command=self.abrir_criacao_item_ciclo,
            relief="raised",
            bd=3,
            activebackground="#E38B2B",
            activeforeground="white",
            padx=25,
            pady=10
        )
        btn_adicionar_item.pack(pady=8)

        btn_abrir_sond = tk.Button(
            self,
            text="Abrir Equipamento na Sond",
            bg="#C85A17",
            fg="#E3DDD2",
            font=("Lucida Console", 11, "bold"),
            command=lambda equipamento=equipamento: self.abrir_item_sond(equipamento["nome_eq"],equipamento["ids"]),
            relief="raised",
            bd=3,
            activebackground="#E38B2B",
            activeforeground="white",
            padx=15
        )
        btn_abrir_sond.pack(pady=(0,12))

        self.dados_equipamento = obter_equipamento_por_id(self.equip_id)
        self.exibir_dados_equipamento()

        self.itens_ciclo = obter_itens_ciclo_vida_por_equipamento(self.equip_id)
        self.exibir_lista_itens()

        self.frame_esquerdo_container.bind("<Enter>", self._bind_scroll_events_esquerdo)
        self.frame_esquerdo_container.bind("<Leave>", self._unbind_scroll_events_esquerdo)

        self.frame_direito.bind("<Enter>", self._bind_scroll_events_direito)
        self.frame_direito.bind("<Leave>", self._unbind_scroll_events_direito)


    # SCROLL ESQUERDO:
    def _on_mousewheel_windows_esquerdo(self, event):
        self.canvas_esquerdo.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_esquerdo(self, event):
        if event.num == 4:
            self.canvas_esquerdo.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas_esquerdo.yview_scroll(1, "units")

    def _bind_scroll_events_esquerdo(self, event=None):
        self.canvas_esquerdo.bind_all("<MouseWheel>", self._on_mousewheel_windows_esquerdo)
        self.canvas_esquerdo.bind_all("<Button-4>", self._on_mousewheel_linux_esquerdo)
        self.canvas_esquerdo.bind_all("<Button-5>", self._on_mousewheel_linux_esquerdo)

    def _unbind_scroll_events_esquerdo(self, event=None):
        self.canvas_esquerdo.unbind_all("<MouseWheel>")
        self.canvas_esquerdo.unbind_all("<Button-4>")
        self.canvas_esquerdo.unbind_all("<Button-5>")

    # SCROLL DIREITO:
    def _on_mousewheel_windows_direito(self, event):
        self.canvas_direito.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_direito(self, event):
        if event.num == 4:
            self.canvas_direito.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas_direito.yview_scroll(1, "units")

    def _bind_scroll_events_direito(self, event=None):
        self.canvas_direito.bind_all("<MouseWheel>", self._on_mousewheel_windows_direito)
        self.canvas_direito.bind_all("<Button-4>", self._on_mousewheel_linux_direito)
        self.canvas_direito.bind_all("<Button-5>", self._on_mousewheel_linux_direito)

    def _unbind_scroll_events_direito(self, event=None):
        self.canvas_direito.unbind_all("<MouseWheel>")
        self.canvas_direito.unbind_all("<Button-4>")
        self.canvas_direito.unbind_all("<Button-5>")

    def abrir_criacao_item_ciclo(self):
        nova_janela = TelaCriacaoCiclo(self, equipamento_id=self.equipamento["id"], callback_atualizar=self.carregar_itens_ciclo)
        nova_janela.grab_set()

    def exibir_dados_equipamento(self):
        for widget in self.scroll_frame_esquerdo.winfo_children():
            widget.destroy()

        if not self.dados_equipamento:
            lbl = tk.Label(self.scroll_frame_esquerdo, text="Equipamento não encontrado.",
                        font=("Courier New", 14), bg="#EDE6D6", fg="red")
            lbl.pack(pady=20)
            return

        campos = [
            ("Nome", "nome_eq"),
            ("Tipo", "tipo"),
            ("Modelo", "modelo"),
            ("Setor", "setor"),
            ("Status", "status"),
            ("Número Série", "numero_serie"),
            ("Fabricante", "fabricante"),
            ("Modelo Técnico", "modelo_tecnico"),
            ("Data Aquisição", "data_aquisicao"),
            ("Última Calibração", "ultima_calibracao"),
            ("Periodicidade", "periodicidade"),
            ("Status Calibração", "status_calibr"),
            ("Sigla", "sigla_eq"),
            ("Extra Info", "extra_info"),
            ("Id no Banco de Dados", "id"),  # <-- campo adicionado aqui, por último
        ]

        for label_text, key in campos:
            valor = self.dados_equipamento.get(key, "N/A")
            frame_linha = tk.Frame(self.scroll_frame_esquerdo, bg="#EDE6D6")
            frame_linha.pack(fill=tk.X, padx=15, pady=5)

            lbl_nome = tk.Label(frame_linha, text=f"{label_text}:", font=("Courier New", 10, "bold"),
                                bg="#EDE6D6", anchor="w")
            lbl_nome.pack(fill=tk.X, anchor="w")

            linha = tk.Frame(frame_linha, bg="#B5AC99", height=1)
            linha.pack(fill=tk.X, pady=(0, 2))

            lbl_valor = tk.Label(frame_linha, text=str(valor), font=("Courier New", 10),
                                bg="#EDE6D6", anchor="w", justify="left", wraplength=500)
            lbl_valor.pack(fill=tk.X, anchor="w")


    def exibir_lista_itens(self):
        # Limpa frame direito para reconstruir
        for widget in self.frame_direito.winfo_children():
            widget.destroy()

        titulo = tk.Label(self.frame_direito, text="Itens do Ciclo de Vida",
                            font=("Courier New", 16, "bold"), bg="#E3DDD2", fg="#333333")
        titulo.pack(pady=10)

        frame_lista = tk.Frame(self.frame_direito, bg="#E3DDD2")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_direito = tk.Canvas(frame_lista, bg="#E3DDD2", highlightthickness=0)
        self.scrollbar_direito = ttk.Scrollbar(frame_lista, orient="vertical", command=self.canvas_direito.yview)
        self.scroll_frame_direito = tk.Frame(self.canvas_direito, bg="#E3DDD2")

        self.scroll_frame_direito.bind(
            "<Configure>",
            lambda e: self.canvas_direito.configure(scrollregion=self.canvas_direito.bbox("all"))
        )

        window_id_direito = self.canvas_direito.create_window((0, 0), window=self.scroll_frame_direito, anchor="nw")

        def ajustar_largura_conteudo_direito(event):
            self.canvas_direito.itemconfig(window_id_direito, width=event.width)

        self.canvas_direito.bind("<Configure>", ajustar_largura_conteudo_direito)
        self.canvas_direito.configure(yscrollcommand=self.scrollbar_direito.set)

        self.canvas_direito.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_direito.pack(side=tk.RIGHT, fill=tk.Y)

        for item in self.itens_ciclo:
            frame_item = tk.Frame(self.scroll_frame_direito, bg="#E3DDD2")
            frame_item.pack(fill=tk.X, pady=4, padx=5)

            # Define 4 colunas agora: tipo, data, editar, excluir
            frame_item.columnconfigure(0, weight=5, uniform="col")
            frame_item.columnconfigure(1, weight=2, uniform="col")
            frame_item.columnconfigure(2, weight=2, uniform="col")
            frame_item.columnconfigure(3, weight=1, uniform="col")

            def ao_clicar(event, item=item):
                TelaDescricaoItem(self, self.equipamento["nome_eq"], item)

            if item.get('valor', '') == None:
                valor = f"{item.get('valor', '')}"
            else:
                valor = f"R${item.get('valor', '')}"

            # Tipo + fornecedor + valor
            texto_tipo = f"{item.get('tipo_item', '')}\n{item.get('fornecedor', '')}\n{valor}"
            frame_tipo = tk.Frame(frame_item, bg="#C7C1A1", bd=1, relief="ridge")
            frame_tipo.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
            frame_tipo.bind("<Button-1>", ao_clicar)

            lbl_tipo = tk.Label(
                frame_tipo,
                text=texto_tipo,
                font=("Courier New", 10, "bold"),  # fonte menor para caber
                bg="#C7C1A1",
                anchor="w",
                justify="left",
                wraplength=300
            )
            lbl_tipo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            lbl_tipo.bind("<Button-1>", ao_clicar)

            # Data
            frame_data = tk.Frame(frame_item, bg="#C7C1A1", bd=1, relief="ridge")
            frame_data.grid(row=0, column=1, sticky="nsew", padx=(2, 2))
            frame_data.bind("<Button-1>", ao_clicar)

            try:
                data_dt = datetime.strptime(item['data'], "%Y-%m-%d")
                data_brasil = data_dt.strftime("%d-%m-%Y")
            except Exception:
                data_brasil = item.get('data', '')

            lbl_data = tk.Label(frame_data, text=data_brasil, font=("Courier New", 12, "bold"),
                                bg="#C7C1A1", anchor="center", justify="center")
            lbl_data.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            lbl_data.bind("<Button-1>", ao_clicar)

            # Botão Editar
            btn_editar = tk.Button(
                frame_item,
                text="Editar",
                font=("Courier New", 10, "bold"),
                bg="#A6A38D",
                fg="black",
                relief="raised",
                bd=2,
                command=lambda item=item: self.abrir_edicao_item(item['id'])
            )
            btn_editar.grid(row=0, column=2, padx=(5, 2), pady=2, sticky="nsew")

            # Botão Excluir
            btn_excluir = tk.Button(
                frame_item,
                text="✘",  # ícone ou "Excluir"
                font=("Courier New", 10, "bold"),
                bg="#C94C4C",
                fg="white",
                relief="raised",
                bd=2,
                command=lambda item=item: self.excluir_item(item['id'])
            )
            btn_excluir.grid(row=0, column=3, padx=(2, 0), pady=2, sticky="nsew")




    def carregar_itens_ciclo(self):
        self.itens_ciclo = obter_itens_ciclo_vida_por_equipamento(self.equip_id)
        self.exibir_lista_itens()

    def abrir_edicao_item(self, item_id):
        TelaEdicaoCiclo(self, item_id, callback=self.carregar_itens_ciclo)

    def abrir_item_sond(self, nome_equip,sond_id):
        webbrowser.open_new_tab(f"https://www.sond.com.br/ativos/perfil/{nome_equip}/{sond_id}/")

    def excluir_item(self, item_id):
        item = next((i for i in self.itens_ciclo if i['id'] == item_id), None)
        if not item:
            messagebox.showerror("Erro", "Item não encontrado para exclusão.")
            return

        resposta = messagebox.askyesno(
            "Confirmação",
            f"Tem certeza que deseja excluir o item '{item['tipo_item']}' do ciclo de vida?"
        )
        if resposta:
            excluir_item(item_id)
            self.carregar_itens_ciclo()