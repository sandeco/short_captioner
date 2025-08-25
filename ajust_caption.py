import copy
import json
import os
from moviepy import VideoFileClip, CompositeVideoClip, TextClip


class CaptionProcessor:
    """
    Classe para processar legendas e agrupar palavras em fases/frases.
    
    Esta classe oferece métodos para:
    - Adicionar fases às palavras baseado em regras de agrupamento
    - Agrupar palavras por fase em frases completas
    - Processar dados de transcrição para criação de legendas
    """
    
    def __init__(self, words_per_line=3, gap_threshold=1.0):
        """
        Inicializa o processador de legendas.
        
        Args:
            words_per_line (int): Número de palavras por linha/fase
            gap_threshold (float): Limiar de tempo (segundos) para forçar nova fase
        """
        self.words_per_line = words_per_line
        self.gap_threshold = gap_threshold
        self.processed_words = []
        self.grouped_phrases = []
    
    def add_phase_to_words(self, words_dataframe):
        """
        Adiciona uma chave 'phase' a cada dicionário de palavra baseado em regras de agrupamento.

        Args:
            words_dataframe (list): Lista de dicionários, onde cada dicionário
                                    representa uma palavra com chaves 'word', 'start' e 'end'.

        Returns:
            list: Nova lista de dicionários com a chave 'phase' adicionada.
        """
        # Cria uma cópia para evitar modificar a lista original
        processed_words = copy.deepcopy(words_dataframe)
        
        phase_counter = 1
        words_in_current_phase = 0
        
        for i, word_data in enumerate(processed_words):
            
            # Verifica condições para iniciar uma nova fase
            if (
                i > 0 and 
                (words_in_current_phase >= self.words_per_line or 
                 (word_data["start"] - processed_words[i - 1]["end"] >= self.gap_threshold))
            ):
                words_in_current_phase = 0
                phase_counter += 1

            # Atribui o número da fase atual
            word_data["phase"] = phase_counter
            words_in_current_phase += 1
            
            # Força uma nova fase para a próxima palavra se a atual termina com pontuação
            if any(char in word_data["word"] for char in [".", "?", "!"]) and words_in_current_phase <= self.words_per_line:
                phase_counter += 1
                words_in_current_phase = 0
        
        self.processed_words = processed_words
        return processed_words

    def group_words_by_phase(self, words_with_phases=None):
        """
        Agrupa palavras por fase e cria frases com timing e confiança.
        
        Args:
            words_with_phases (list, optional): Lista de dicionários com palavras que possuem a chave 'phase'.
                                               Se None, usa self.processed_words.
            
        Returns:
            list: Lista de dicionários com frases agrupadas por fase, contendo:
                  - 'phase': número da fase
                  - 'text': texto completo da fase
                  - 'start': tempo de início da primeira palavra
                  - 'end': tempo de fim da última palavra
                  - 'confidence': confiança média das palavras na fase
                  - 'word_count': número de palavras na fase
        """
        if words_with_phases is None:
            words_with_phases = self.processed_words
            
        if not words_with_phases:
            return []
        
        # Agrupa palavras por fase
        phases = {}
        
        for word_data in words_with_phases:
            phase_num = word_data['phase']
            
            if phase_num not in phases:
                phases[phase_num] = []
            
            phases[phase_num].append(word_data)
        
        # Cria frases para cada fase
        grouped_phrases = []
        
        for phase_num in sorted(phases.keys()):
            words_in_phase = phases[phase_num]
            
            # Extrai o texto de cada palavra e junta
            text_parts = [word['word'] for word in words_in_phase]
            full_text = ' '.join(text_parts)
            
            # Calcula timing
            start_time = words_in_phase[0]['start']
            end_time = words_in_phase[-1]['end']
            
            # Calcula confiança média
            confidences = [word['confidence'] for word in words_in_phase]
            avg_confidence = sum(confidences) / len(confidences)
            
            # Cria o dicionário da frase
            phrase_data = {
                'phase': phase_num,
                'text': full_text,
                'start': start_time,
                'end': end_time,
                'duration': round(end_time - start_time, 2),
                'confidence': round(avg_confidence, 4),
                'word_count': len(words_in_phase),
                'words': words_in_phase  # Mantém as palavras originais para referência
            }
            
            grouped_phrases.append(phrase_data)
        
        self.grouped_phrases = grouped_phrases
        return grouped_phrases
    
    def process_caption_data(self, words_dataframe):
        """
        Processa dados de legenda completos: adiciona fases e agrupa em frases.
        
        Args:
            words_dataframe (list): Lista de dicionários com dados das palavras
            
        Returns:
            tuple: (palavras_com_fases, frases_agrupadas)
        """
        words_with_phases = self.add_phase_to_words(words_dataframe)
        grouped_phrases = self.group_words_by_phase(words_with_phases)
        
        return words_with_phases, grouped_phrases
    
    def get_phrase_by_phase(self, phase_number):
        """
        Retorna uma frase específica pelo número da fase.
        
        Args:
            phase_number (int): Número da fase desejada
            
        Returns:
            dict or None: Dados da frase ou None se não encontrada
        """
        for phrase in self.grouped_phrases:
            if phrase['phase'] == phase_number:
                return phrase
        return None
    
    def get_phrases_in_time_range(self, start_time, end_time):
        """
        Retorna frases que ocorrem dentro de um intervalo de tempo.
        
        Args:
            start_time (float): Tempo de início em segundos
            end_time (float): Tempo de fim em segundos
            
        Returns:
            list: Lista de frases no intervalo especificado
        """
        phrases_in_range = []
        
        for phrase in self.grouped_phrases:
            # Verifica se há sobreposição com o intervalo
            if phrase['start'] < end_time and phrase['end'] > start_time:
                phrases_in_range.append(phrase)
        
        return phrases_in_range
    
    def print_summary(self):
        """
        Imprime um resumo das frases processadas.
        """
        if not self.grouped_phrases:
            print("Nenhuma frase processada ainda.")
            return
        
        print("=== RESUMO DAS FRASES AGRUPADAS ===")
        for phrase in self.grouped_phrases:
            print(f"Fase {phrase['phase']}: '{phrase['text']}'")
            print(f"  Timing: {phrase['start']}s - {phrase['end']}s (duração: {phrase['duration']}s)")
            print(f"  Confiança: {phrase['confidence']:.4f} | Palavras: {phrase['word_count']}")
            print()
        
        print(f"Total de frases: {len(self.grouped_phrases)}")
        total_duration = max(phrase['end'] for phrase in self.grouped_phrases) if self.grouped_phrases else 0
        print(f"Duração total: {total_duration:.2f}s")


