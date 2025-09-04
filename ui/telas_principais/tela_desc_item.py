import tkinter as tk 
from datetime import datetime

class TelaDescricaoItem(tk.Toplevel):
    def __init__(self, master, nome_equipamento, item):
        super().__init__(master)
        self.title("Descrição do Item")
        self.configure(bg="#F5F1E9")
        self.resizable(False, False)

        # Posicionar próximo da janela principal
        if master is not None:
            master_x = master.winfo_x()
            master_y = master.winfo_y()
            pos_x = master_x + 50
            pos_y = master_y + 50
            self.geometry(f"800x400+{pos_x}+{pos_y}")
        else:
            self.geometry("800x400")

        # Converter a data para dd-mm-yyyy
        try:
            data_dt = datetime.strptime(item['data'], "%Y-%m-%d")
            data_formatada = data_dt.strftime("%d-%m-%Y")
        except Exception:
            data_formatada = item['data']

        # Título
        titulo_texto = f"{nome_equipamento} - {item['tipo_item']} - ({data_formatada})"
        titulo = tk.Label(self,
                          text=titulo_texto,
                          font=("Courier New", 16, "bold"),
                          bg="#EDE6D6",
                          fg="#333333",
                          relief="raised",
                          bd=2,
                          padx=10,
                          pady=5)
        titulo.pack(pady=(20, 5))

        # Info Especial
        info_especial = item.get("info_especial")
        if info_especial:
            info_label = tk.Label(self, 
                                  text=f"Info Especial: {info_especial}",
                                  font=("Courier New", 11, "italic"),
                                  bg="#F0EAD6",
                                  fg="#363636",
                                  wraplength=700,
                                  justify="left")
            info_label.pack(padx=15, pady=(10, 10), fill=tk.X)

        # Descrição (ocupando menos espaço)
        descricao_frame = tk.Frame(self, bg="#EDE6D6", bd=2, relief="sunken")
        descricao_frame.pack(padx=30, pady=(10,5), fill=tk.BOTH, expand=False)

        descricao_label = tk.Label(descricao_frame,
                                   text=item.get("descricao", "Sem descrição."),
                                   font=("Courier New", 12),
                                   bg="#EDE6D6",
                                   justify="left",
                                   anchor="nw",
                                   wraplength=700,
                                   height=10)  # altura fixa para ocupar menos espaço
        descricao_label.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

        # Quadro para fornecedor e valor lado a lado
        info_frame = tk.Frame(self, bg="#F5F1E9")
        info_frame.pack(padx=30, pady=(5,20), fill=tk.X)

        # Fornecedor
        fornecedor_frame = tk.Frame(info_frame, bg="#DDE6D6", bd=1, relief="sunken")
        fornecedor_frame.pack(side="left", expand=True, fill=tk.BOTH, padx=(0,10))
        tk.Label(fornecedor_frame, text="Fornecedor:", font=("Courier New", 11, "bold"), bg="#DDE6D6").pack(anchor="w", padx=5, pady=(5,0))
        tk.Label(fornecedor_frame, text=item.get("fornecedor") or "-", font=("Courier New", 11), bg="#DDE6D6", wraplength=300, justify="left").pack(anchor="w", padx=5, pady=(0,5))

        # Valor
        valor_frame = tk.Frame(info_frame, bg="#DDE6D6", bd=1, relief="sunken")
        valor_frame.pack(side="left", expand=True, fill=tk.BOTH, padx=(10,0))
        tk.Label(valor_frame, text="Valor (R$):", font=("Courier New", 11, "bold"), bg="#DDE6D6").pack(anchor="w", padx=5, pady=(5,0))

        # Formatação BRL
        raw_valor = item.get("valor")
        if raw_valor not in [None, ""]:
            try:
                numero = float(raw_valor)
                valor_formatado = f"R${numero:,.2f}"  # Ex.: 150,000.00
                valor_formatado = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")  # R$150.000,00
            except ValueError:
                valor_formatado = f"R${raw_valor}"
        else:
            valor_formatado = "-"

        tk.Label(valor_frame, text=valor_formatado, font=("Courier New", 11), bg="#DDE6D6").pack(anchor="w", padx=5, pady=(0,5))

