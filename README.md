# Sistema de Triagem Hospitalar Inteligente

## Visão Geral
Sistema de pré-triagem para classificação de risco em hospitais utilizando Inteligência Artificial, com foco em acessibilidade e otimização do fluxo de pacientes.

## Problema
A superlotação em emergências hospitalares causa longas esperas e potenciais atrasos no atendimento de casos graves. Este projeto propõe um agente inteligente para auxiliar na pré-triagem, classificando pacientes por nível de risco com base em dados iniciais.

## Objetivos
- Otimizar a alocação de recursos hospitalares
- Identificar pacientes críticos mais rapidamente
- Reduzir tempo de espera através de triagem automatizada
- Garantir acessibilidade total do sistema

## Arquitetura PEAS
- **P (Performance)**: Acurácia, F1-Score, redução do tempo de espera
- **E (Environment)**: Sistema simulado de admissão de emergência
- **A (Atuadores)**: Interface com classificação de risco e score de confiança
- **S (Sensores)**: Formulário digital para entrada de dados do paciente

## Tecnologias Utilizadas
- Python 3.8+
- Scikit-learn (modelos de ML)
- Pandas (manipulação de dados)
- Flask (interface web)
- HTML/CSS com acessibilidade WCAG
- Matplotlib/Seaborn (visualização)

## Estrutura do Projeto
```
├── data/                   # Datasets e dados processados
├── models/                 # Modelos treinados
├── src/                    # Código fonte
│   ├── agents/            # Agentes inteligentes
│   ├── ml/                # Modelos de machine learning
│   ├── utils/             # Utilitários
│   └── web/               # Interface web
├── tests/                 # Testes
├── docs/                  # Documentação
└── requirements.txt       # Dependências
```

## Classificação de Risco (Manchester)
- **Vermelho**: Emergência (atendimento imediato)
- **Amarelo**: Urgente (atendimento em até 1 hora)
- **Verde**: Não Urgente (atendimento em até 4 horas)

## Instalação
```bash
pip install -r requirements.txt
```

## Execução
```bash
python src/main.py
```

## Contribuição
Este projeto foi desenvolvido como parte do estudo de Inteligência Artificial, baseado nos conceitos de Russell e Norvig.
