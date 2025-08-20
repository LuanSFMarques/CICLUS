import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from controllers.equipamento_controller import info_para_plano_calibr

class TelaPlanoDeCalibracao(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Plano de Calibração - Próximos 30 dias")
        self.geometry("800x400")
        self.configure(bg="#F5F1E9")
        self.resizable(True, True)

        # Label topo
        lbl = tk.Label(self, text="Equipamentos com calibração vencendo nos próximos 30 dias",
                       font=("Courier New", 14, "bold"), bg="#F5F1E9", relief="raised", padx=5, pady=10)
        lbl.pack(pady=10)

        # Frame para Text e Scrollbar
        frame_text = tk.Frame(self)
        frame_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text = tk.Text(frame_text, wrap=tk.WORD, font=("Courier New", 11))
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_text, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.config(yscrollcommand=scrollbar.set)

        # Carrega dados e exibe
        self.listar_equipamentos_proximos_30_dias()

    def listar_equipamentos_proximos_30_dias(self):
        try:
            equipamentos = info_para_plano_calibr()
        except Exception as e:
            self.text.insert(tk.END, f"Erro ao carregar equipamentos: {e}")
            self.text.config(state="disabled")  # trava edição mesmo em caso de erro
            return

        hoje = datetime.today()
        limite = hoje + timedelta(days=30)

        relatorio = []
        for eq in equipamentos:
            try:
                data_ult_cal = eq.get("ultima_calibracao")
                periodicidade = eq.get("periodicidade")

                if not data_ult_cal or not periodicidade:
                    continue

                dt_ult_cal = datetime.strptime(data_ult_cal, "%Y-%m-%d")
                dt_prox_cal = dt_ult_cal + relativedelta(months=int(periodicidade))

                if hoje <= dt_prox_cal <= limite:
                    dias_restantes = (dt_prox_cal - hoje).days + 1
                    dia = "dia" if dias_restantes == 1 else "dias"
                    relatorio.append(
                        f"{eq['nome_eq']}\t\tPróxima calibração em {dt_prox_cal.strftime('%d/%m/%Y')}"
                        f"\t\t\t(em {dias_restantes} {dia})\n"
                    )
            except Exception as e:
                print(f"Erro ao processar {eq}: {e}")
                continue

        if not relatorio:
            self.text.insert(tk.END, "Nenhum equipamento com calibração vencendo nos próximos 30 dias.")
        else:
            self.text.insert(tk.END, "".join(relatorio))

        self.text.config(state="disabled")
