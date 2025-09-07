import os
import json
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv


# --- CLASSE PRINCIPAL ---
class ViralClipFinder:
    """
    Uma classe para encontrar momentos virais em legendas de vídeo usando a API Gemini.
    """

    @staticmethod
    def analyze_subtitle(subtitle: str, min_duration: int = 30, max_duration: int = 60) -> Dict[str, Any]:
        """
        Método estático para analisar uma legenda e identificar momentos virais.
        
        Args:
            subtitle: Texto da legenda do vídeo
            min_duration: Duração mínima dos cortes em segundos (padrão: 9 segundos)
            max_duration: Duração máxima dos cortes em segundos (padrão: 15 segundos)
            
        Returns:
            Dicionário JSON com os momentos virais identificados
        """
        # Carrega variáveis de ambiente do arquivo .env
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("A chave de API do Google Gemini é obrigatória. "
                           "Configure GEMINI_API_KEY no arquivo .env ou passe como parâmetro.")
        
        # Configura o cliente Gemini
        genai.configure(api_key=api_key)
        
        # Configuração para garantir que a saída seja JSON
        generation_config = genai.GenerationConfig(response_mime_type="application/json")
        
        # Cria o modelo
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=generation_config
        )
        
        # Obtém o template do prompt
        prompt_template = ViralClipFinder._get_prompt_template(subtitle, min_duration, max_duration)
        
        try:
                    
            # Faz a chamada para o Gemini
            response = model.generate_content(prompt_template)
            
            # Extrai o JSON da resposta
            result_text = response.text
            
            # Tenta fazer o parse do JSON
            try:
                # Remove possíveis delimitadores de código markdown
                if "```json" in result_text:
                    json_start = result_text.find("```json") + 7
                    json_end = result_text.find("```", json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif "```" in result_text:
                    json_start = result_text.find("```") + 3
                    json_end = result_text.find("```", json_start)
                    result_text = result_text[json_start:json_end].strip()
                
                return json.loads(result_text)
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao fazer parse do JSON: {e}")
                print(f"📝 Resposta recebida: {result_text}")
                raise ValueError("Resposta inválida da API do Gemini")
                
        except Exception as e:
            print(f"❌ Erro ao analisar legenda: {e}")
            raise

    @staticmethod
    def _get_prompt_template(subtitle: str, min_duration: int, max_duration: int) -> str:
        """Carrega o template do prompt mestre que criamos."""
        # O prompt completo que definimos na conversa anterior vai aqui.
        prompt =  f"""

#REGRA OBRIGATÓRIA:
 - OS TRECHOS DEVEM TER ENTRE 30 E 60 SEGUNDOS DE DURAÇÃO.
 - A DURAÇÃO DEVE SER SEMPRE MAIOR QUE 30 SEGUNDOS.
 - EXTRAIA O MÁXIMO QUE CONSEGUIR
 - TENTE EXTRAIR COM MAIOR DURAÇÃO POSSÍVEL.

Estou repetindo as regras para você entender. Se você
retornar um trecho com uma duração fora do intervalo especificado,
você será DESPEDIDO.

## [Seção 1: Persona e Contexto]
Você é um "AI Viral SHORT/REELs Analyst", 
um especialista em análise de conteúdo de vídeo. 
Sua função combina a de um editor de vídeo para shorts
no youtube ou Reels no instagram, com a de um 
copywriter sênior com doutorado em Marketing Digital. 
Você não apenas identifica trechos com potencial de viralização, 
mas também cria títulos e descrições otimizados para a máxima 
taxa de cliques (CTR) e engajamento, aplicando métodos analíticos 
e criativos. Seu objetivo final é gerar um pacote de conteúdo 
completo e pronto para publicação.

## [Seção 2: A Tarefa Principal]
Sua tarefa é analisar a transcrição de um vídeo, 
fornecida na tag `<legenda>`, 
e identificar os melhores "momentos virais". 
Para cada momento, você deve criar um título 
e uma descrição prontos para postagem, 
seguindo rigorosamente as diretrizes e o formato de saída especificado.

**IMPORTANTE:** Os cortes devem ter entre {min_duration} e {max_duration} segundos de duração. 
Esses cortes serão usados para criar um ou vários shorts 
do vídeo cortes para o youtube ou reels no instagram.


## [Seção 3: Critérios para Escolha dos "Momentos Virais"]
Para selecionar os melhores trechos do vídeo, avalie 
a legenda com base nestes critérios:

1. **Duração Ideal:** Trechos entre {min_duration} e {max_duration} segundos (prioridade alta)
2. **Emoção Forte:** Momentos que geram reação emocional intensa
3. **Declarações Impactantes ou Polêmicas:** Frases que desafiam crenças ou geram debate
4. **Momentos "Aha!" / Insights Chave:** Revelações surpreendentes ou aprendizados valiosos
5. **Ganchos e Cliffhangers:** Trechos que deixam o espectador querendo mais
6. **Humor e Momentos Inesperados:** Conteúdo engraçado ou surpreendente
7. **Conselhos Práticos e Dicas Rápidas:** Informações acionáveis e úteis
8. **Storytelling Conciso:** Narrativas completas dentro do tempo limite

## [Seção 4: Diretrizes para Criação de Títulos e Descrições]
Ao criar o `titulo_sugestivo` e a `descricao_para_postagem` para cada corte, 
você DEVE aplicar os seguintes princípios de copywriting e SEO, derivados de uma análise de alta performance:

1.  **Combine Curiosidade com Clareza:** O título deve ser intrigante, prometendo um insight inesperado ("O segredo que..."), mas também deixar claro qual o tema e o valor para o espectador.
2.  **Prometa Valor Imediato:** Deixe explícito o que a pessoa vai ganhar ao assistir: um guia, uma dica prática, uma revelação surpreendente sobre um tema de seu interesse.
3.  **Use Formatos de Sucesso:** Empregue fórmulas comprovadas que geram cliques, como:
    * **Listas e Números:** "5 Erros que Você Comete em..."
    * **Perguntas Diretas:** "Você Está Usando a Ferramenta X Errado?"
    * **Como Fazer (How-to):** "Como Fazer [Tarefa Difícil] em 5 Minutos"
    * **Declaração Contraintuitiva:** "Por que [Prática Comum] é uma Perda de Tempo"
4.  **Seja Conciso e Impactante:** Prefira títulos curtos e diretos. Cada palavra deve ter um propósito. Remova o excesso.
5.  **Gere Apelo Emocional/Pessoal:** Sempre que possível, conecte o tema a emoções universais como medo, esperança, segurança, curiosidade ou pertencimento. Fale sobre "privacidade" ou "segurança" se o tema permitir.

## [Seção 4.1: Diretrizes para Criação de Texto de Thumbnail]
A técnica central para definir o texto de uma thumbnail se baseia em uma análise 
estratégica do título e da transcrição do próprio vídeo. 
O processo começa com a extração de palavras e frases de alto potencial, 
como os termos-chave do assunto, palavras de poder que 
geram emoção ou curiosidade (ex: "segredo", "erro", "rápido"), 
verbos de ação e números impactantes. Esses termos extraídos são 
então agrupados em diferentes "ganchos" de comunicação, como focar no 
benefício direto para o espectador, despertar a curiosidade sobre um 
mistério ou destacar um resultado específico, preparando o terreno para a criação do texto final.

Com os ganchos definidos, o passo seguinte é criar variações de texto 
extremamente concisas, idealmente com 2 a 5 palavras, 
garantindo máxima legibilidade com fontes grandes e alto contraste. 
A escolha final não deve repetir o título, mas sim complementá-lo, 
adicionando uma camada de emoção ou curiosidade que incentive o clique. 
É fundamental que o texto escolhido seja fiel ao conteúdo do vídeo 
para evitar a prática de clickbait, assegurando que a promessa feita 
na thumbnail seja entregue, o que constrói a confiança e a retenção da audiência a longo prazo.

## [Seção 5: O Input]
Você receberá a legenda completa do vídeo no formato abaixo.

<legenda>
{subtitle}
</legenda>

## [Seção 6: Formato da Saída (MUITO IMPORTANTE)]
Sua resposta DEVE ser um objeto JSON válido, contendo uma lista chamada 
"cortes_virais". Não inclua nenhum texto ou explicação fora do bloco de código JSON. 
Cada item na lista deve ser um objeto com as seguintes chaves:

-   `id`: Identificador único do corte
-   `timestamp_inicio`: Timestamp de início no formato HH:MM:SS.mmm
-   `timestamp_fim`: Timestamp de fim no formato HH:MM:SS.mmm
-   `duracao_minutos_segundos`: Duração do corte em minutos e segundos MM:SS (deve estar entre {min_duration} e {max_duration})
-   `titulo_sugestivo`: Título otimizado para viralização
-   `texto_thumb`: Texto conciso para thumbnail (2-3 palavras, máximo impacto visual)
-   `descricao_para_postagem`: Descrição completa com hashtags
-   `justificativa_interna`: Explicação da escolha
-   `tipo_de_gancho`: Tipo de gancho usado
-   `clima`: Um clima para a thumbnail (tenso, alegre, duvida.. etc)
-   `expressao_facial`: Expressão facial para a thumbnail (alegria, tristeza, raiva, desconfiado, gargalhando, sorrindo)
-   `texto_gerar_thumbnail`: Texto para gerar thumbnail, descreva a cena para chamar atenção

#Importante:
- Não use virgula notimestamp inválido: 00:05:05,780. 
- Use ponto no timestamp HH:MM:SS.mmm (válido)

"""
        prompt = prompt + r"""
### [Exemplo de Saída Perfeita]

{
  "cortes_virais": [
    {
      "id": 1,
      "timestamp_inicio": "00:02:10.500",
      "timestamp_fim": "00:02:40.250",
      "duracao_minutos_segundos": "00:30",
      "titulo_sugestivo": "Pare de ensaiar seus discursos agora mesmo",
      "texto_thumb": "PARA AGORA!",
      "descricao_para_postagem": "A maioria dos 'gurus' de oratória manda você ensaiar por horas, mas isso pode estar destruindo sua autenticidade. Existe uma forma melhor de se preparar.\n\nVocê concorda ou discorda? Me conta sua experiência nos comentários!\n\n#oratoria #falarempublico #dicasdeoratoria #comunicacaoeficaz #desenvolvimentopessoal",
      "justificativa_interna": "Usa uma declaração forte e contraintuitiva para desafiar uma crença comum, gerando curiosidade e debate imediatos. Título criado seguindo a diretriz 4.3.",
      "tipo_de_gancho": "Declaração Polêmica"
    }
  ]
}
"""
        return prompt

