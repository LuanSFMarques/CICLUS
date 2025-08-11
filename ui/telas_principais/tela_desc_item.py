import tkinter as tk 
from datetime import datetime

class TelaDescricaoItem(tk.Toplevel):
    def __init__(self, master, nome_equipamento, item):
        #print(item)
        super().__init__(master)
        self.title("Descrição do Item")
        self.configure(bg="#F5F1E9")
        self.resizable(False, False)

        # Posicionar próximo da janela principal (como sua referência)
        if master is not None:
            master_x = master.winfo_x()
            master_y = master.winfo_y()
            pos_x = master_x + 50
            pos_y = master_y + 50
            self.geometry(f"800x400+{pos_x}+{pos_y}")  # aumento da altura
        else:
            self.geometry("800x400")

        # Converter a data para dd-mm-yyyy
        try:
            data_dt = datetime.strptime(item['data'], "%Y-%m-%d")
            data_formatada = data_dt.strftime("%d-%m-%Y")
        except Exception:
            data_formatada = item['data']

        print("Descricao:", repr(item.get("descricao")))
        print("Info Especial:", repr(item.get("info_especial")))


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

        descricao_frame = tk.Frame(self, bg="#EDE6D6", bd=2, relief="sunken")
        descricao_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)

        descricao_label = tk.Label(descricao_frame,
                                   text=item.get("descricao", "Sem descrição."),
                                   font=("Courier New", 12),
                                   bg="#EDE6D6",
                                   justify="left",
                                   anchor="nw",
                                   wraplength=700,
                                   )
        descricao_label.pack(padx=15, pady=(15,5), fill=tk.BOTH, expand=True)
