import os
import time
import schedule
import pyzipper  # Use pyzipper se pyminizip não estiver funcionando
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Caminhos das pastas para monitoramento
PASTAS_MONITORADAS = ["C:/pasta", "C:/pasta1"]  # Adicione quantas pastas quiser
PASTA_LOGS = "C:/Logs"
SENHA_ZIP = "aldeia123"

# Classe de monitoramento de eventos
class MonitoramentoHandler(FileSystemEventHandler):
    def __init__(self, log_files):
        self.log_files = log_files

    def log_event(self, log_file, message):
        with open(log_file, "a") as f:
            f.write(f"{time.ctime()} - {message}\n")

    def on_modified(self, event):
        if not event.is_directory:
            for log_file in self.log_files:
                if event.src_path.startswith(PASTAS_MONITORADAS[0]):  # Verifica se o evento é para uma das pastas monitoradas
                    self.log_event(log_file, f"Arquivo modificado: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            for log_file in self.log_files:
                if event.src_path.startswith(PASTAS_MONITORADAS[0]):
                    self.log_event(log_file, f"Arquivo criado: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            for log_file in self.log_files:
                if event.src_path.startswith(PASTAS_MONITORADAS[0]):
                    self.log_event(log_file, f"Arquivo deletado: {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory:
            for log_file in self.log_files:
                if event.src_path.startswith(PASTAS_MONITORADAS[0]):
                    self.log_event(log_file, f"Arquivo movido: {event.src_path} -> {event.dest_path}")

# Função para criar um arquivo ZIP protegido por senha com os logs
def criar_zip_protegido():
    data = time.strftime("%Y-%m-%d")
    log_file = os.path.join(PASTA_LOGS, f"log_{data}.txt")
    zip_file = os.path.join(PASTA_LOGS, f"log_{data}.zip")

    if os.path.exists(log_file):
        # Comprime o arquivo de log em um ZIP protegido por senha
        with pyzipper.AESZipFile(zip_file, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(SENHA_ZIP.encode('utf-8'))
            zf.write(log_file, arcname=os.path.basename(log_file))
        print(f"Arquivo ZIP protegido criado: {zip_file}")

        # Remove o arquivo de log original após criar o ZIP
        os.remove(log_file)

# Função para iniciar o monitoramento das pastas
def iniciar_monitoramento():
    data = time.strftime("%Y-%m-%d")
    log_files = [os.path.join(PASTA_LOGS, f"log_{data}_{i}.txt") for i, _ in enumerate(PASTAS_MONITORADAS)]

    # Logar o primeiro acesso para cada pasta
    for log_file in log_files:
        if not os.path.exists(log_file):
            with open(log_file, "a") as f:
                f.write(f"{time.ctime()} - Primeiro acesso à pasta\n")

    event_handler = MonitoramentoHandler(log_files)
    observer = Observer()

    for pasta in PASTAS_MONITORADAS:
        observer.schedule(event_handler, pasta, recursive=True)

    observer.start()
    print(f"Iniciando monitoramento das pastas: {', '.join(PASTAS_MONITORADAS)}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Agendar criação diária do ZIP às 18:30
schedule.every().day.at("18:30").do(criar_zip_protegido)

# Função principal para iniciar o script
if __name__ == "__main__":
    if not os.path.exists(PASTA_LOGS):
        os.makedirs(PASTA_LOGS)
    iniciar_monitoramento()
    while True:
        schedule.run_pending()
        time.sleep(60)  # Espera 60 segundos para verificar novamente
