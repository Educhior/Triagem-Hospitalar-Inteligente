
# Sistema de Triagem Hospitalar Inteligente

## Visão Geral
Sistema inteligente para pré-triagem hospitalar, utilizando IA para classificar pacientes por risco, otimizar o fluxo de atendimento e garantir acessibilidade total.

## Problema
Emergências hospitalares frequentemente enfrentam superlotação, causando atrasos no atendimento de casos graves. Este sistema visa automatizar a triagem, priorizando pacientes críticos e otimizando recursos.

## Objetivos
- Otimizar a alocação de recursos hospitalares
- Identificar rapidamente pacientes críticos
- Reduzir o tempo de espera com triagem automatizada
- Garantir acessibilidade digital para todos os usuários

## Arquitetura PEAS
- **Performance**: Acurácia, F1-Score, redução do tempo de espera
- **Environment**: Ambiente simulado de emergência hospitalar
- **Atuadores**: Interface web com classificação de risco e score de confiança
- **Sensores**: Formulário digital para entrada dos dados do paciente

## Tecnologias Utilizadas
- Python 3.8+
- Scikit-learn (machine learning)
- Pandas (manipulação de dados)
- Flask (aplicação web)
- HTML/CSS (acessibilidade WCAG)
- Matplotlib/Seaborn (visualização)

## Estrutura do Projeto
```
├── data/                   # Datasets e dados processados
├── models/                 # Modelos treinados
├── src/                    # Código fonte
│   ├── agents/             # Agentes inteligentes
│   ├── ml/                 # Modelos de machine learning
│   ├── utils/              # Utilitários
│   └── web/                # Interface web (Flask)
├── tests/                  # Testes
├── docs/                   # Documentação
└── requirements.txt        # Dependências
```

## Classificação de Risco (Manchester)
- **Vermelho**: Emergência (atendimento imediato)
- **Amarelo**: Urgente (atendimento em até 1 hora)
- **Verde**: Não Urgente (atendimento em até 4 horas)

---

## Como Adicionar Dados para Treinamento

1. **Adicionar dados manualmente:**
   - Coloque arquivos CSV com dados de pacientes na pasta `data/`.
   - O formato esperado inclui colunas como: `idade`, `sexo`, `pressao_sistolica`, `pressao_diastolica`, `frequencia_cardiaca`, `saturacao_oxigenio`, `temperatura`, `dor_peito`, `dificuldade_respiratoria`, `febre`, `tontura`, `vomito`, `dor_abdominal`, `risk_level`.

2. **Gerar dados sintéticos automaticamente:**
   - Execute o sistema em modo demonstração:
     ```bash
     python main.py --demo
     ```
   - O sistema irá gerar e salvar um dataset sintético em `data/sample_dataset.csv`.

3. **Utilizar o dataset para treinamento:**
   - Use o arquivo gerado ou seus próprios dados para treinar modelos em `src/ml/`.
   - Adapte scripts de treinamento conforme necessário para ler os dados do arquivo desejado.

---

## Como Executar o Projeto

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Execute o sistema:**
   ```bash
   python main.py
   ```
   O sistema web estará disponível em http://localhost:5000

3. **Modo demonstração (opcional):**
   ```bash
   python main.py --demo
   ```
   Isso irá rodar uma simulação de triagem e gerar estatísticas no terminal.

---

## Contribuição
Este projeto foi desenvolvido como parte de estudos em Inteligência Artificial, baseado nos conceitos de Russell e Norvig. Sinta-se livre para contribuir!
