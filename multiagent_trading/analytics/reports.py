import json

class PerformanceReport:
    """
    Gera sumários de performance em formato de texto/JSON (preparando para PDF).
    """
    def __init__(self, backtest_results):
        self.results = backtest_results

    def generate_summary(self):
        metrics = self.results.get("metrics", {})
        summary = f"""
        ========================================
        MATF - RELATÓRIO DE PERFORMANCE (v1.1)
        ========================================
        Valor Final do Portfólio: ${metrics.get('final_value', 0):,.2f}
        Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.4f}
        Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%

        Total de Trocas: {len(self.results.get('pnl', []))}
        ========================================
        """
        return summary

    def save_to_file(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.generate_summary())
