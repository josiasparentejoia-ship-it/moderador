"""
Script de teste de configuração
Verifica se todas as variáveis estão configuradas corretamente
"""
import os
import sys
from pathlib import Path

# Fix encoding no Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from dotenv import load_dotenv
    import aiogram
except ImportError:
    print("[X] Erro: Dependencias nao instaladas!")
    print("Execute: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

def test_config():
    """Testa configuração do bot"""
    print("\n>>> VERIFICANDO CONFIGURACAO\n")
    print("="*60)

    errors = []
    warnings = []

    # Teste 1: BOT_TOKEN
    print("\n[1] BOT_TOKEN")
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        errors.append("BOT_TOKEN nao encontrado no .env")
        print("   [X] Nao configurado")
    elif ":" not in bot_token or len(bot_token) < 40:
        errors.append("BOT_TOKEN parece invalido")
        print(f"   [!] Token suspeito: {bot_token[:20]}...")
    else:
        print(f"   [OK] Configurado: {bot_token[:20]}...{bot_token[-10:]}")

    # Teste 2: GROUP_ID
    print("\n[2] GROUP_ID")
    group_id = os.getenv("GROUP_ID")
    if not group_id:
        errors.append("GROUP_ID nao encontrado no .env")
        print("   [X] Nao configurado")
    else:
        try:
            gid = int(group_id)
            if gid > 0:
                warnings.append("GROUP_ID deve ser negativo (ex: -1002603662151)")
                print(f"   [!] Positivo (deveria ser negativo): {gid}")
            else:
                print(f"   [OK] Configurado: {gid}")
        except ValueError:
            errors.append("GROUP_ID deve ser um numero")
            print(f"   [X] Invalido: {group_id}")

    # Teste 3: WEBAPP_URL
    print("\n[3] WEBAPP_URL")
    webapp_url = os.getenv("WEBAPP_URL")
    if not webapp_url:
        errors.append("WEBAPP_URL nao encontrado no .env")
        print("   [X] Nao configurado")
    elif not webapp_url.startswith("https://"):
        warnings.append("WEBAPP_URL deveria usar HTTPS em producao")
        print(f"   [!] Sem HTTPS: {webapp_url}")
    else:
        print(f"   [OK] Configurado: {webapp_url}")

    # Teste 4: ADMIN_ID
    print("\n[4] ADMIN_ID")
    admin_id = os.getenv("ADMIN_ID")
    if not admin_id:
        errors.append("ADMIN_ID nao encontrado no .env")
        print("   [X] Nao configurado")
    elif admin_id == "0" or admin_id == "seu_user_id_aqui":
        errors.append("ADMIN_ID nao foi alterado do valor padrao")
        print(f"   [X] Valor padrao: {admin_id}")
        print("   >>> Envie mensagem para @userinfobot no Telegram")
        print("   >>> Cole o numero que ele responder no .env")
    else:
        try:
            aid = int(admin_id)
            if aid < 0:
                warnings.append("ADMIN_ID normalmente e positivo")
                print(f"   [!] Negativo (suspeito): {aid}")
            else:
                print(f"   [OK] Configurado: {aid}")
        except ValueError:
            errors.append("ADMIN_ID deve ser um numero")
            print(f"   [X] Invalido: {admin_id}")

    # Teste 5: Arquivo config.json
    print("\n[5] config.json")
    config_file = Path("config.json")
    if config_file.exists():
        print("   [OK] Arquivo existe")
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"   [i] {len(config.get('periodic_messages', []))} mensagens periodicas")
                print(f"   [i] {len(config.get('admin_ids', []))} admins configurados")
        except Exception as e:
            warnings.append(f"Erro ao ler config.json: {e}")
            print(f"   [!] Erro ao ler: {e}")
    else:
        print("   [i] Sera criado automaticamente no primeiro uso")

    # Teste 6: Dependências
    print("\n[6] Dependencias Python")
    try:
        import aiogram
        print(f"   [OK] aiogram {aiogram.__version__}")
    except ImportError:
        errors.append("aiogram nao instalado")
        print("   [X] aiogram nao instalado")

    try:
        import dotenv
        print(f"   [OK] python-dotenv instalado")
    except ImportError:
        errors.append("python-dotenv nao instalado")
        print("   [X] python-dotenv nao instalado")

    # Resumo
    print("\n" + "="*60)
    print("\n>>> RESUMO")
    print("="*60)

    if not errors and not warnings:
        print("\n[OK] TUDO CERTO! Pode executar o bot:")
        print("     python bot_admin.py")
        return True

    if warnings:
        print(f"\n[!] {len(warnings)} AVISO(S):")
        for w in warnings:
            print(f"    - {w}")

    if errors:
        print(f"\n[X] {len(errors)} ERRO(S):")
        for e in errors:
            print(f"    - {e}")
        print("\n>>> COMO CORRIGIR:")
        print("    1. Edite o arquivo .env")
        print("    2. Configure as variaveis corretamente")
        print("    3. Execute este teste novamente: python test_config.py")
        return False

    return len(errors) == 0

if __name__ == "__main__":
    try:
        success = test_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[X] Teste cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
