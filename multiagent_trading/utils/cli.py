import argparse
import sys
import subprocess
import os

def main():
    parser = argparse.ArgumentParser(description="MATF CLI - Multi-Agent Trading Framework")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: dashboard
    subparsers.add_parser("dashboard", help="Inicia o Dashboard Streamlit")

    # Comando: api
    subparsers.add_parser("api", help="Inicia a API REST FastAPI")

    # Comando: backtest
    backtest_parser = subparsers.add_parser("backtest", help="Executa um backtest de exemplo")
    backtest_parser.add_argument("--example", type=str, default="examples/backtest_example.py", help="Caminho para o script de backtest")

    args = parser.parse_args()

    if args.command == "dashboard":
        print("A iniciar o Dashboard...")
        subprocess.run(["streamlit", "run", "multiagent_trading/analytics/dashboard.py"])

    elif args.command == "api":
        print("A iniciar a API...")
        subprocess.run(["uvicorn", "multiagent_trading.core.api:app", "--reload"])

    elif args.command == "backtest":
        print(f"A executar backtest: {args.example}")
        subprocess.run(["python3", args.example])

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
