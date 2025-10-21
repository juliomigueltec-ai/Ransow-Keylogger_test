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
