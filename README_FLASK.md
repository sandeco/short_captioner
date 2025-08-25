# Short Captioner - Aplicação Flask

Uma aplicação web Flask para adicionar legendas automáticas a vídeos usando dados de transcrição JSON.

## 🚀 Funcionalidades

- **Interface Web Intuitiva**: Upload de vídeos e arquivos JSON via drag & drop
- **Processamento Assíncrono**: Processamento em background com atualizações de status em tempo real
- **Configurações Personalizáveis**: 
  - Tamanho e cor da fonte
  - Número de palavras por linha
  - Posicionamento das legendas
  - Seleção de fontes disponíveis
- **Prévia das Legendas**: Visualize como as legendas ficarão antes do processamento
- **Download Automático**: Download direto do vídeo processado

## 📋 Pré-requisitos

- Python 3.12+
- Dependências listadas em `pyproject.toml`

## 🛠️ Instalação

1. **Instale as dependências:**
```bash
uv sync
```

2. **Execute a aplicação:**
```bash
python run_flask.py
```

3. **Acesse no navegador:**
```
http://localhost:5000
```

## 📁 Estrutura do Projeto

```
short_captioner/
├── app.py                 # Aplicação Flask principal
├── run_flask.py          # Script para executar a aplicação
├── short_captioner.py    # Classe principal de legendagem
├── ajust_caption.py      # Processador de legendas
├── video_captioner.py    # Wrapper para compatibilidade
├── templates/
│   └── index.html        # Interface web principal
├── static/
│   └── style.css         # Estilos adicionais
├── fonts/                # Fontes TTF/OTF
├── uploads/              # Arquivos enviados (criado automaticamente)
└── outputs/              # Vídeos processados (criado automaticamente)
```

## 🎯 Como Usar

### 1. **Upload de Arquivos**
- Selecione ou arraste um arquivo de vídeo (MP4, AVI, MOV, MKV, WEBM)
- Selecione ou arraste um arquivo JSON com a transcrição

### 2. **Configurar Legendas**
- **Tamanho da Fonte**: 20-120px
- **Cor do Texto**: Branco, Amarelo, Vermelho, Azul, Verde
- **Palavras por Linha**: 1-8 palavras
- **Margem Inferior**: 50-300px
- **Fonte**: Selecione entre as fontes disponíveis
- **Contorno**: Cor e largura do contorno

### 3. **Prévia (Opcional)**
- Clique em "Prévia das Legendas" para ver como ficarão as primeiras frases

### 4. **Processar**
- Clique em "Processar Vídeo"
- Acompanhe o progresso na barra de status
- Faça o download quando concluído

## 📊 Formato do JSON

O arquivo JSON deve conter uma lista de objetos com as seguintes chaves:

```json
[
  {
    "word": "Palavra",
    "start": 0.0,
    "end": 0.5,
    "confidence": 0.95
  }
]
```

- `word`: Texto da palavra
- `start`: Tempo de início em segundos
- `end`: Tempo de fim em segundos  
- `confidence`: Confiança da transcrição (0-1)

## 🔧 API Endpoints

### `POST /upload`
Upload de vídeo e JSON para processamento

### `GET /status/<process_id>`
Verifica status do processamento

### `GET /download/<process_id>`
Download do vídeo processado

### `POST /preview`
Prévia das legendas de um arquivo JSON

### `GET /fonts`
Lista fontes disponíveis

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente
- `FLASK_ENV`: Ambiente (development/production)
- `FLASK_DEBUG`: Modo debug (True/False)

### Limites
- Tamanho máximo de arquivo: 500MB
- Tipos de vídeo aceitos: MP4, AVI, MOV, MKV, WEBM
- Tipos de arquivo aceitos: JSON

## 🐛 Solução de Problemas

### Erro de Fonte
Se uma fonte não for encontrada, a aplicação usará a fonte padrão do sistema.

### Erro de Processamento
- Verifique se o arquivo JSON está no formato correto
- Certifique-se de que o vídeo não está corrompido
- Verifique os logs no terminal para mais detalhes

### Erro de Upload
- Verifique o tamanho do arquivo (máx. 500MB)
- Certifique-se de que os tipos de arquivo são suportados

## 🔄 Migração do Código Original

O projeto mantém compatibilidade com o código original através da classe `VideoCaptioner`:

```python
from video_captioner import VideoCaptioner

captioner = VideoCaptioner(
    video_file="video.mp4",
    output_file="output.mp4",
    json_file="words.json"
)

captioner.generate()
```

## 📝 Notas Técnicas

- Processamento assíncrono usando threads Python
- Interface responsiva com Bootstrap 5
- Atualizações de status em tempo real via polling
- Limpeza automática de recursos após processamento
- Suporte a drag & drop para melhor UX

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request
