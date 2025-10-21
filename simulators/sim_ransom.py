"""
Simulador de Ransomware com criptografia real *segura* (aplica-se APENAS aos arquivos criados pelo script).

USO SEGURO:
- Execute somente em VM isolada com snapshot.
- Este script opera apenas dentro de ./sandbox/originals/
- Antes de criptografar é necessária confirmação manual (digite YES).
- A chave é salva em ./sandbox/chave.key — guarde-a para descriptografar.

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
