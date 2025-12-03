#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy Progress Monitor - Monitora progresso do deploy em tempo real com dashboard HTML
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class DeployMonitor:
    """Monitora o progresso de deploy com dashboard HTML"""
    
    def __init__(self):
        self.state = {
            "status": "iniciando",
            "current_step": 0,
            "total_steps": 0,
            "start_time": time.time(),
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_total": 0,
            "messages": [],
            "estimated_completion": None,
            "phase": "preparation"
        }
        
        self.phases = [
            {"name": "Preparação", "description": "Inicializando ambiente", "duration_est": 10},
            {"name": "Testes Unitários", "description": "Executando testes básicos", "duration_est": 30},
            {"name": "Testes de Rotas", "description": "Validando todas as rotas", "duration_est": 45},
            {"name": "Testes de Temas", "description": "Testando 8 variações de tema", "duration_est": 60},
            {"name": "Testes de Pré-Deploy", "description": "Checagem final antes do deploy", "duration_est": 30},
            {"name": "Validação Final", "description": "Validando integridade completa", "duration_est": 20},
            {"name": "Deploy", "description": "Enviando para produção", "duration_est": 15}
        ]
        
        self.state["total_steps"] = len(self.phases)
        
    def add_message(self, msg, level="info"):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.state["messages"].append({
            "time": timestamp,
            "level": level,
            "text": msg
        })
        
    def update_step(self, step_index, passed_tests=None, failed_tests=None):
        """Atualiza passo atual"""
        self.state["current_step"] = step_index + 1
        if passed_tests is not None:
            self.state["tests_passed"] = passed_tests
        if failed_tests is not None:
            self.state["tests_failed"] = failed_tests
            
        # Calcula ETA
        elapsed = time.time() - self.state["start_time"]
        if self.state["current_step"] > 0:
            avg_time_per_step = elapsed / self.state["current_step"]
            remaining_steps = self.state["total_steps"] - self.state["current_step"]
            estimated_remaining = int(avg_time_per_step * remaining_steps)
            self.state["estimated_completion"] = datetime.now() + timedelta(seconds=estimated_remaining)
            
    def get_percentage(self):
        """Retorna percentual de progresso"""
        if self.state["total_steps"] == 0:
            return 0
        return (self.state["current_step"] / self.state["total_steps"]) * 100
    
    def save_dashboard(self, filename="deploy_progress.json"):
        """Salva estado para ser lido pelo dashboard HTML"""
        self.state["percentage"] = self.get_percentage()
        self.state["timestamp"] = datetime.now().isoformat()
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def generate_html_dashboard(self):
        """Gera HTML interativo do dashboard"""
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deploy Progress - BMA_VF</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 800px;
            padding: 40px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        
        .header p {{
            color: #666;
            font-size: 0.95em;
        }}
        
        .progress-section {{
            margin-bottom: 40px;
        }}
        
        .progress-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            color: #666;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 24px;
            background: #f0f0f0;
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid #e0e0e0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .progress-percentage {{
            font-weight: bold;
            color: #333;
        }}
        
        .eta {{
            margin-top: 10px;
            padding: 12px;
            background: #f5f5f5;
            border-radius: 8px;
            font-size: 0.9em;
            color: #666;
            border-left: 4px solid #667eea;
        }}
        
        .phases {{
            display: grid;
            gap: 12px;
            margin-bottom: 30px;
        }}
        
        .phase {{
            padding: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 16px;
            transition: all 0.3s ease;
        }}
        
        .phase.active {{
            border-color: #667eea;
            background: #f9f9ff;
        }}
        
        .phase.completed {{
            border-color: #4caf50;
            background: #f1f8f4;
        }}
        
        .phase-icon {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            flex-shrink: 0;
            font-size: 1.2em;
        }}
        
        .phase-icon.pending {{
            background: #ccc;
        }}
        
        .phase-icon.active {{
            background: #667eea;
            animation: spin 1s linear infinite;
        }}
        
        .phase-icon.completed {{
            background: #4caf50;
        }}
        
        .phase-content {{
            flex: 1;
        }}
        
        .phase-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 4px;
        }}
        
        .phase-description {{
            font-size: 0.85em;
            color: #999;
        }}
        
        .test-results {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 20px;
        }}
        
        .result-card {{
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #e0e0e0;
        }}
        
        .result-card.passed {{
            background: #f1f8f4;
            border-color: #4caf50;
        }}
        
        .result-card.failed {{
            background: #fef5f5;
            border-color: #f44336;
        }}
        
        .result-value {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        
        .result-passed {{
            color: #4caf50;
        }}
        
        .result-failed {{
            color: #f44336;
        }}
        
        .result-label {{
            font-size: 0.85em;
            color: #666;
        }}
        
        .messages {{
            background: #f5f5f5;
            border-radius: 8px;
            padding: 16px;
            max-height: 200px;
            overflow-y: auto;
            font-size: 0.85em;
            font-family: 'Courier New', monospace;
        }}
        
        .message {{
            margin-bottom: 8px;
            padding: 6px;
            border-left: 3px solid #ccc;
            padding-left: 12px;
        }}
        
        .message.info {{
            border-color: #667eea;
            color: #667eea;
        }}
        
        .message.success {{
            border-color: #4caf50;
            color: #4caf50;
        }}
        
        .message.error {{
            border-color: #f44336;
            color: #f44336;
        }}
        
        .message.warning {{
            border-color: #ff9800;
            color: #ff9800;
        }}
        
        .message-time {{
            color: #999;
            font-size: 0.8em;
        }}
        
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.5em;
            }}
            
            .test-results {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Deploy Progress Monitor</h1>
            <p>BMA_VF - Belarmino Monteiro Advogado</p>
        </div>
        
        <div class="progress-section">
            <div class="progress-label">
                <span>Progresso Geral</span>
                <span class="progress-percentage">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%">0%</div>
            </div>
            <div class="eta">
                <strong>ETA de Conclusão:</strong> Calculando...
            </div>
        </div>
        
        <div class="test-results">
            <div class="result-card passed">
                <div class="result-value result-passed">0</div>
                <div class="result-label">Testes Passaram</div>
            </div>
            <div class="result-card failed">
                <div class="result-value result-failed">0</div>
                <div class="result-label">Testes Falharam</div>
            </div>
        </div>
        
        <div class="phases" id="phases"></div>
        
        <div>
            <h3 style="margin-bottom: 12px; color: #333;">Log de Progresso:</h3>
            <div class="messages" id="messages">
                <div class="message info">
                    <span class="message-time">[00:00:00]</span> Sistema iniciado
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const phases = {json.dumps([p['name'] for p in self.phases])};
        
        async function updateDashboard() {{
            try {{
                const response = await fetch('deploy_progress.json');
                const data = await response.json();
                
                // Atualiza barra de progresso
                const percentage = data.percentage || 0;
                const progressBar = document.querySelector('.progress-fill');
                progressBar.style.width = percentage + '%';
                progressBar.textContent = Math.round(percentage) + '%';
                
                // Atualiza label
                document.querySelector('.progress-percentage').textContent = Math.round(percentage) + '%';
                
                // Atualiza ETA
                if (data.estimated_completion) {{
                    const etaDate = new Date(data.estimated_completion);
                    const etaHour = String(etaDate.getHours()).padStart(2, '0');
                    const etaMin = String(etaDate.getMinutes()).padStart(2, '0');
                    document.querySelector('.eta').innerHTML = 
                        `<strong>ETA de Conclusão:</strong> ${{etaHour}}:${{etaMin}}`;
                }}
                
                // Atualiza resultados
                const passedCard = document.querySelector('.result-card.passed .result-value');
                const failedCard = document.querySelector('.result-card.failed .result-value');
                passedCard.textContent = data.tests_passed || 0;
                failedCard.textContent = data.tests_failed || 0;
                
                // Atualiza fases
                const phasesContainer = document.getElementById('phases');
                phasesContainer.innerHTML = phases.map((phase, idx) => {{
                    let status = 'pending';
                    let iconSymbol = '○';
                    
                    if (idx < data.current_step) {{
                        status = 'completed';
                        iconSymbol = '✓';
                    }} else if (idx === data.current_step - 1) {{
                        status = 'active';
                        iconSymbol = '⟳';
                    }}
                    
                    return `
                        <div class="phase ${{status}}">
                            <div class="phase-icon ${{status}}">${{iconSymbol}}</div>
                            <div class="phase-content">
                                <div class="phase-name">${{phase}}</div>
                            </div>
                        </div>
                    `;
                }}).join('');
                
                // Atualiza mensagens
                const messagesContainer = document.getElementById('messages');
                messagesContainer.innerHTML = (data.messages || []).map(msg => 
                    `<div class="message ${{msg.level}}">
                        <span class="message-time">[${{msg.time}}]</span> ${{msg.text}}
                    </div>`
                ).join('');
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
            }} catch (e) {{
                console.log('Aguardando dados...');
            }}
        }}
        
        // Atualiza a cada 1 segundo
        setInterval(updateDashboard, 1000);
        updateDashboard();
    </script>
</body>
</html>
"""
        
        return html


def generate_dashboard():
    """Gera dashboard HTML"""
    monitor = DeployMonitor()
    html = monitor.generate_html_dashboard()
    
    with open("deploy_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Dashboard gerado: deploy_dashboard.html")


if __name__ == "__main__":
    generate_dashboard()
