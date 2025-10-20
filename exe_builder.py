import subprocess

def build_with_pyinstaller():
    comando = [
        "pyinstaller",
        "--onedir",
        "--noconsole",
        "--icon=Assets/logos/ciclus_logo_laranja.ico",
        "--add-data=Assets;Assets",
        "--name=ciclus",
        "main.py"
    ]

    try:
        subprocess.run(comando, check=True)
        print("Build concluída com sucesso!")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar o PyInstaller:")
        print(e)

if __name__ == "__main__":
    build_with_pyinstaller()
