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
* [Simulador de Ransomware](#ransonware)
* [Simulador de Keylogger](#keylogger)
* [Artefatos e suas Localizações](#artefatos-e-suas-localizações)
* [Boas Práticas para Ethical Hacking (Uso)](#boas-práticas-para-ethical-hacking)
* [Detecção e Prevenção de Danos](#detecção-e-prevenção-de-danos)

  
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

**Status de Desenvolvimento:** O código-fonte deste simulador está disponível para revisão no branch [https://github.com/juliomigueltec-ai/Ransow-Keylogger_test/blob/047b0111b4759023962bdd75ce16a15607c7994e/simulators/sim_ransom.py]

### Comportamento


- Backup dos originais em `sandbox/backup_before_encrypt/` antes da criptografia.
  
- Requer digitar `YES` (case-sensitive) para executar `--encrypt`.

- A chave é salva em 'sandbox/chave.key'. **Atenção:** a chave usada pelo simulador **NÃO deve** ser comitada em repositórios públicos nem compartilhada. Mantenha `sandbox/chave.key` em local seguro (offline) e adicione 'sandbox/' ao '.gitignore'.
- 

### Arquivos gerados


- 'sandbox/originals/' — arquivos originais (ou sobrescritos se criptografados)
  
- 'sandbox/backup_before_encrypt/' — cópia dos arquivos antes da encriptação
  
- 'sandbox/chave.key' — chave Fernet (mantenha offline / **não comitar**)
- 

### Flags


python sim_ransom_real.py --prepare --count 5           # cria arquivos de teste

python sim_ransom_real.py --genkey                      # gera chave (sandbox/chave.key)

python sim_ransom_real.py --encrypt                     # criptografa (requer confirmação YES)

python sim_ransom_real.py --decrypt                     # descriptografa usando sandbox/chave.key

[2. Simulador de Keylogger](#keylogger)


### Aplicabilidade


Demonstrar ciclo de um keylogger sem capturar teclas furtivas — replay a partir de sandbox/input_simulated_keystrokes.txt, logging em sandbox/log.txt e preview de exfiltração.

**Status de Desenvolvimento:** O código-fonte deste simulador está disponível para revisão no branch [simulators/sim_keylogger_simple_simulator.py.](https://github.com/juliomigueltec-ai/Ransow-Keylogger_test/blob/047b0111b4759023962bdd75ce16a15607c7994e/simulators/sim_keylogger_simple_simulator.py.)


### Comportamento


Não captura entradas do sistema.

Envio SMTP bloqueado por padrão; precisa ALLOW_KEYLOGGER_SEND=1 ou confirm_send=true no smtp_config.json.


### Arquivos gerados


sandbox/input_simulated_keystrokes.txt — arquivo de entrada simulado (gerado automaticamente se ausente)

sandbox/log.txt — log com timestamps

sandbox/outgoing_email_preview.txt — preview do que seria exfiltrado

sandbox/smtp_config.json — template SMTP (se gerado)


### Flags


python sim_keylogger_simple_simulator.py --simulate            # replay dos keystrokes simulados

python sim_keylogger_simple_simulator.py --interactive         # digitação com consentimento

python sim_keylogger_simple_simulator.py --preview-email       # gera preview do payload (sem enviar)

python sim_keylogger_simple_simulator.py --write-smtp-tpl      # cria sandbox/smtp_config.json


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
- 

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

