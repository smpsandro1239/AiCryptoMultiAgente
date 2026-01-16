import pandas as pd
import matplotlib.pyplot as plt

def generate_report(results, memory):
    """
    Generate a simple textual report of trading performance and decisions.
    """
    report = "=== MATF Trading Report ===\n"
    pnl = results.get("pnl", [])
    if pnl:
        report += f"Initial Value: {pnl[0]}\n"
        report += f"Final Value: {pnl[-1]}\n"
        report += f"Total Return: {((pnl[-1] / pnl[0]) - 1) * 100:.2f}%\n"

    report += "\n=== Key Decisions ===\n"
    for entry in memory.memory:
        report += f"- {entry['key']}: {entry['value']}\n"

    return report

def plot_performance(results, output_path="performance.png"):
    """
    Plot PnL history.
    """
    pnl = results.get("pnl", [])
    if not pnl:
        return

    plt.figure(figsize=(10, 6))
    plt.plot(pnl, label="Portfolio Value")
    plt.title("MATF Performance")
    plt.xlabel("Ticks")
    plt.ylabel("Value")
    plt.legend()
    plt.savefig(output_path)
    plt.close()
