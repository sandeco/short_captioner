# Short Captioner

Sistema de legendagem automática para vídeos curtos com interface web.

## Funcionalidades

- **Upload de vídeos**: Interface web para envio de arquivos de vídeo
- **Legendagem automática**: Geração de legendas com posicionamento personalizado
- **Múltiplas fontes**: Suporte a diferentes tipos de fonte (Bangers, Gotham, Knewave)
- **Processamento em tempo real**: Visualização do progresso de processamento
- **Download automático**: Vídeo legendado disponível para download

## Tecnologias Utilizadas

- **Backend**: Python, Flask
- **Processamento de vídeo**: MoviePy
- **Frontend**: HTML, CSS, JavaScript
- **Fontes**: TTF personalizadas

## Estrutura do Projeto

```
short_captioner/
├── app.py                 # Aplicação Flask principal
├── short_captioner.py     # Lógica de legendagem (versão 1)
├── short_captionerV2.py   # Lógica de legendagem (versão 2)
├── ajust_caption.py       # Ajustes de legendas
├── templates/
│   └── index.html         # Interface web
├── static/
│   ├── css/
│   │   └── style.css      # Estilos da aplicação
│   └── js/
│       └── scripts.js     # Scripts JavaScript
├── fonts/                 # Fontes TTF
├── uploads/               # Vídeos enviados
└── outputs/               # Vídeos processados
```

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd short_captioner
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python app.py
```

4. Acesse `http://localhost:5000` no navegador

## Uso

1. Acesse a interface web
2. Faça upload de um arquivo de vídeo
3. Aguarde o processamento
4. Baixe o vídeo legendado

## Dependências Principais

- Flask
- MoviePy
- Outras dependências listadas em `pyproject.toml`

## Licença

Projeto privado.