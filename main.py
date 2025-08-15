# main.py
import sys
import traceback
import tkinter as tk
from tkinter import messagebox

from ui.telas_principais.tela_equipamentos import TelaPrincipal
from helpers import log_msg
import data.db  # nosso novo módulo

def main():
    try:
        log_msg("Aplicativo iniciado")

        # Garantir que a conexão é criada no início
        data.db.get_connection()

        app = TelaPrincipal()

        # Fechar a conexão ao fechar a janela
        app.protocol("WM_DELETE_WINDOW", lambda: fechar_app(app))

        app.mainloop()

    except Exception as e:
        error_msg = f"Erro inesperado ao iniciar o aplicativo:\n{e}"
        print(error_msg)
        traceback.print_exc()
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro", error_msg)
        sys.exit(1)

def fechar_app(app):
    data.db.close_connection()
    app.destroy()

if __name__ == "__main__":
    main()
