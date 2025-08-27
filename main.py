# main.py
import sys
import traceback
import tkinter as tk
from tkinter import messagebox

from ui.telas_principais.tela_equipamentos import TelaPrincipal
from helpers import log_msg

def main():
    try:
        log_msg("Aplicativo iniciado")

        app = TelaPrincipal()
        app.mainloop()

    except Exception as e:
        error_msg = f"Erro inesperado ao iniciar o aplicativo:\n{e}"
        print(error_msg)
        traceback.print_exc()
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
