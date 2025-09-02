document.addEventListener('DOMContentLoaded', async function () {
    // --- Verificação e Restauração de Sessão ---
    async function checkAndRestoreSession() {
        try {
            const response = await fetch('/check-session', { credentials: 'include' });
            const data = await response.json();

            if (response.ok && data.has_session) {
                // Restaura os dados da sessão na UI
                currentFilename = data.filename;
                videoPreviewOriginal.src = data.video_url;
                transcriptionText.value = data.srt_content;

                console.log('Sessão restaurada com sucesso:');
                console.log('- Filename:', currentFilename);
                console.log('- Video URL:', data.video_url);
                console.log('- Video element src:', videoPreviewOriginal.src);
                console.log('- Video element:', videoPreviewOriginal);

                // Mostra a seção de edição
                showSection(editSection);
                transcriptionDisplay.classList.remove('d-none');
                actionsSection.classList.remove('d-none');
                
                // Restaura os clipes virais se existirem
                console.log('Verificando viral_clips na sessão:', data.viral_clips);
                if (data.viral_clips && data.viral_clips.cortes_virais && data.viral_clips.cortes_virais.length > 0) {
                    console.log('Restaurando clipes virais:', data.viral_clips.cortes_virais.length, 'clipes encontrados');
                    displayViralClips(data.viral_clips.cortes_virais, data.parametros_corte);
                } else {
                    console.log('Nenhum clipe viral encontrado na sessão restaurada');
                }
            } else {
                // Se não houver sessão, mostra a tela de upload
                showSection(uploadSection);
            }
        } catch (error) {
            console.error('Erro ao verificar a sessão:', error);
            showError('Não foi possível verificar a sessão. Por favor, comece do início.');
            showSection(uploadSection); // Fallback para a tela de upload
        }
    }

    const uploadForm = document.getElementById('upload-form');
    const uploadSection = document.getElementById('upload-section');
    const editSection = document.getElementById('edit-section');
    const resultSection = document.getElementById('result-section');
    const loadingSection = document.getElementById('loading-section');
    const errorSection = document.getElementById('error-section');
    const loadingText = document.getElementById('loading-text');

    const videoPreviewOriginal = document.getElementById('video-preview-original');
    const transcriptionDisplay = document.getElementById('transcription-display');
    const actionsSection = document.getElementById('actions-section');
    const transcriptionText = document.getElementById('transcription-text');
    const findViralClipsBtn = document.getElementById('find-viral-clips-btn');
    const newProjectBtn = document.getElementById('new-project-btn');
    
    let currentFilename = '';

    await checkAndRestoreSession();

    // --- Event Listeners ---
    newProjectBtn.addEventListener('click', async function() {
        if (confirm('Tem certeza que deseja começar um novo projeto? Todos os dados atuais serão perdidos.')) {
            await startNewProject();
        }
    });

    // --- Gerenciamento de UI ---
    function showSection(section) {
        [uploadSection, editSection, resultSection, loadingSection].forEach(s => s.classList.add('d-none'));
        section.classList.remove('d-none');
    }

    function showError(message) {
        errorSection.textContent = message;
        errorSection.classList.remove('d-none');
    }

    function hideError() {
        errorSection.classList.add('d-none');
    }

    function showSuccess(message) {
        // Cria uma mensagem de sucesso temporária
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insere no início do card-body
        const cardBody = document.querySelector('.card-body');
        cardBody.insertBefore(successDiv, cardBody.firstChild);
    }

    function hideSuccess() {
        const successAlert = document.querySelector('.alert-success');
        if (successAlert) {
            successAlert.remove();
        }
    }

    // --- Fluxo da Aplicação ---

    // 1. Upload do vídeo
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        hideError();
        showSection(loadingSection);
        loadingText.textContent = 'Enviando e transcrevendo o vídeo... Isso pode levar alguns minutos.';

        const formData = new FormData(this);

        try {
            const response = await fetch('/upload', {
                credentials: 'include',
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                currentFilename = data.filename;
                videoPreviewOriginal.src = data.video_url;
                transcriptionText.value = data.srt_content;

                showSection(editSection);
                transcriptionDisplay.classList.remove('d-none');
                actionsSection.classList.remove('d-none');
            } else {
                throw new Error(data.message || 'Ocorreu um erro no servidor.');
            }
        } catch (error) {
            showError(`Erro no upload: ${error.message}`);
            showSection(uploadSection);
        }
    });

    // 2. Encontrar clipes virais
    findViralClipsBtn.addEventListener('click', async function() {
        hideError();
        console.log('Botão Extrair Shorts clicado');
        
        // Mostra o spinner no botão e o desabilita
        const originalButtonText = this.innerHTML;
        this.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analisando...`;
        this.disabled = true;

        try {
            console.log('Fazendo requisição para /find_shorts...');
            const response = await fetch('/find_shorts', {
                credentials: 'include',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log('Status da resposta:', response.status);
            const data = await response.json();
            console.log('Resposta completa da API:', data);
            console.log('Tipo de data:', typeof data);
            console.log('Chaves disponíveis:', Object.keys(data));
            console.log('Status:', data.status);
            console.log('Estrutura viral_clips:', data.viral_clips);
            console.log('Tipo de viral_clips:', typeof data.viral_clips);
            console.log('cortes_virais direto:', data.cortes_virais);
            console.log('parametros_corte:', data.parametros_corte);
            
            // Debug adicional
            console.log('=== DEBUG ESTRUTURA COMPLETA ===');
            console.log('data.viral_clips:', data.viral_clips);
            if (data.viral_clips) {
                console.log('data.viral_clips.cortes_virais:', data.viral_clips.cortes_virais);
                console.log('Tipo de cortes_virais:', typeof data.viral_clips.cortes_virais);
                console.log('É array?', Array.isArray(data.viral_clips.cortes_virais));
                if (Array.isArray(data.viral_clips.cortes_virais)) {
                    console.log('Quantidade de clipes:', data.viral_clips.cortes_virais.length);
                    console.log('Primeiro clipe:', data.viral_clips.cortes_virais[0]);
                }
            }
            console.log('=== FIM DEBUG ===');

            if (response.ok) {
                // Verificar se temos parâmetros de corte para redimensionar os vídeos
                const parametrosCorte = data.parametros_corte;
                console.log('Parâmetros de corte:', parametrosCorte);
                
                // Corrigir: acessar cortes_virais dentro de viral_clips
                const viralClips = data.viral_clips;
                console.log('Viral clips completo:', viralClips);
                
                if (viralClips && viralClips.cortes_virais && viralClips.cortes_virais.length > 0) {
                    console.log('Chamando displayViralClips com:', viralClips.cortes_virais.length, 'clipes');
                    displayViralClips(viralClips.cortes_virais, parametrosCorte);
                } else {
                    console.error('➤➤ Nenhum clipe viral encontrado na resposta');
                    console.error('➤➤ data.cortes_virais:', data.cortes_virais);
                    console.error('➤➤ viralClips.cortes_virais:', viralClips?.cortes_virais);
                    showError('Nenhum clipe viral foi encontrado. Verifique se o vídeo contém conteúdo adequado.');
                }
            } else {
                throw new Error(data.message || 'Ocorreu um erro ao analisar os clipes.');
            }
        } catch (error) {
            showError(`Erro: ${error.message}`);
        } finally {
            // Restaura o botão ao estado original
            this.innerHTML = originalButtonText;
            this.disabled = false;
        }
    });

    

    function displayViralClips(clips, parametrosCorte = null) {
        const container = document.getElementById('viral-clips-container');
        const section = document.getElementById('viral-clips-section');
        
        container.innerHTML = ''; // Limpa o container
    
        // Limpa qualquer aviso de crop anterior para não duplicar
        const existingCropInfo = section.querySelector('#crop-info');
        if (existingCropInfo) {
            existingCropInfo.remove();
        }
    
        if (!clips || clips.length === 0) {
            container.innerHTML = '<p>Nenhum clipe viral foi sugerido.</p>';
            section.classList.remove('d-none');
            return;
        }
    
        // Adicionar indicador visual de que o vídeo será redimensionado (se aplicável)
        if (parametrosCorte) {
            const cropInfo = document.createElement('div');
            cropInfo.id = 'crop-info';
            cropInfo.innerHTML = `
                <i class="fas fa-crop-alt"></i> 
                <strong>Vídeo redimensionado para formato 9:16:</strong> 
                <br>• Área de foco: ${parametrosCorte.width}×${parametrosCorte.height}px
                <br>• Centro: (${parametrosCorte.x_center}, ${parametrosCorte.y_center})
                <br>• Proporção: 9:16 (formato Shorts)
            `;
            // Insere o aviso antes do container de clipes, dentro da seção principal
            section.insertBefore(cropInfo, container);
        }
    
        // 1. Inicia uma string vazia para acumular o HTML
        let allClipsHTML = '';
    
        clips.forEach((clip, index) => {
            const clipId = clip.id;
            const collapseId = `collapse-${clipId}`;

            // 2. Adiciona o HTML COMPLETO de cada clipe à string
            allClipsHTML += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading-${clipId}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                            <strong>${clip.titulo_sugestivo}</strong> (Duração: ${clip.duracao_minutos_segundos})
                        </button>
                    </h2>
                    <div id="${collapseId}" class="accordion-collapse collapse" aria-labelledby="heading-${clipId}" data-bs-parent="#viral-clips-container">
                        <div class="accordion-body text-start">
                            <div class="row mb-3">
                                <div class="col-md-4">
                                    <div class="video-preview-container">
                                        <video 
                                            id="preview-${clipId}" 
                                            class="video-preview-thumbnail" 
                                            preload="metadata"
                                            playsinline
                                            data-start="${clip.timestamp_inicio}" 
                                            data-end="${clip.timestamp_fim}">
                                            <source src="${videoPreviewOriginal.src}" type="video/mp4">
                                        </video>
                                        <div class="video-controls">
                                            <button class="btn btn-sm btn-primary play-preview-btn" data-target="preview-${clipId}">
                                                <i class="fas fa-play"></i> Preview
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-8">
                                    <p><strong>Texto para Thumbnail:</strong> ${clip.texto_thumb}</p>
                                    <p><strong>Descrição:</strong> ${clip.descricao_para_postagem.replace(/\n/g, '<br>')}</p>
                                    <p><strong>Justificativa:</strong> ${clip.justificativa_interna}</p>
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <small class="text-muted">Início: ${clip.timestamp_inicio}</small>
                                            <small class="text-muted">Duração: ${clip.duracao_minutos_segundos}</small>
                                            <small class="text-muted">Fim: ${clip.timestamp_fim}</small>
                                        </div>
                                    </div>
                                    
                                    <!-- Slider duplo para edição de cortes -->
                                    <div class="clip-editor-container mb-3" data-clip-id="${clipId}">
                                        <div class="clip-editor-header mb-2">
                                            <h6 class="mb-1"><i class="fas fa-edit"></i> Editor de Corte</h6>
                                            <div class="time-labels d-flex justify-content-between">
                                                <span class="time-label" id="start-label-${clipId}">Início: 00:00:00.000</span>
                                                <span class="time-label" id="duration-label-${clipId}">Duração: 00:00</span>
                                                <span class="time-label" id="end-label-${clipId}">Fim: 00:00:00.000</span>
                                            </div>
                                        </div>
                                        
                                        <div class="dual-range-slider" id="slider-${clipId}">
                                            <div class="slider-track"></div>
                                            <div class="slider-range"></div>
                                            <input type="range" 
                                                   class="slider-input slider-start" 
                                                   id="start-${clipId}"
                                                   min="0" 
                                                   max="100" 
                                                   value="0"
                                                   step="0.04"
                                                   aria-label="Tempo de início">
                                            <input type="range" 
                                                   class="slider-input slider-end" 
                                                   id="end-${clipId}"
                                                   min="0" 
                                                   max="100" 
                                                   value="100"
                                                   step="0.04"
                                                   aria-label="Tempo de fim">
                                        </div>
                                        
                                        <div class="slider-status mt-2">
                                            <small class="text-muted" id="status-${clipId}">Pronto para edição</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <button class="btn btn-success w-100 generate-video-btn" 
                                clip_id="${clip.id}"
                                data-start="${clip.timestamp_inicio}" 
                                data-end="${clip.timestamp_fim}" 
                                data-title="${clip.titulo_sugestivo}">
                                Gerar Vídeo Final com Legenda
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        // 3. Insere a string HTML completa no container de uma só vez
        container.innerHTML = allClipsHTML;

        // 4. Mostra a seção e inicializa os controles (preview e geração)
        section.classList.remove('d-none');

        console.log('[DEBUG] Chamando setupVideoPreviewControls...');
        setupVideoPreviewControls();
        console.log('[DEBUG] Chamando setupGenerateVideoButtons...');
        setupGenerateVideoButtons();
        console.log('[DEBUG] Chamando setupClipEditors com clips:', clips);
        
        // Usar setTimeout para garantir que os elementos HTML estejam no DOM
        setTimeout(() => {
            setupClipEditors(clips);
        }, 100);

        if (parametrosCorte) {
            setTimeout(() => {
                applyVideoCropping(parametrosCorte);
            }, 200);
        }
    }

    // Configuração dos editores de clipe (sliders duplos)
    async function setupClipEditors(clips) {
        try {
            // Obter duração do vídeo
            const response = await fetch('/get_video_duration');
            const data = await response.json();
            
            if (!response.ok || data.status !== 'success') {
                console.error('Erro ao obter duração do vídeo:', data.message);
                return;
            }
            
            const videoDuration = data.duration;
            
            clips.forEach(clip => {
                setupDualRangeSlider(clip, videoDuration);
            });
        } catch (error) {
            console.error('Erro ao configurar editores de clipe:', error);
        }
    }

    // Configuração individual do slider duplo
    function setupDualRangeSlider(clip, videoDuration) {
        const clipId = clip.id;
        const startSlider = document.getElementById(`start-${clipId}`);
        const endSlider = document.getElementById(`end-${clipId}`);
        const sliderRange = document.querySelector(`#slider-${clipId} .slider-range`);
        const startLabel = document.getElementById(`start-label-${clipId}`);
        const durationLabel = document.getElementById(`duration-label-${clipId}`);
        const endLabel = document.getElementById(`end-label-${clipId}`);
        const statusElement = document.getElementById(`status-${clipId}`);
        
        if (!startSlider || !endSlider) return;

        // Converter timestamps iniciais para segundos
        const initialStart = timestampToSeconds(clip.timestamp_inicio);
        const initialEnd = timestampToSeconds(clip.timestamp_fim);
        
        // Calcular janela dinâmica (±40s)
        const windowMargin = 40;
        const windowMin = Math.max(0, initialStart - windowMargin);
        const windowMax = Math.min(videoDuration, initialEnd + windowMargin);
        const windowRange = windowMax - windowMin;
        
        // Configurar range dos sliders
        startSlider.min = windowMin;
        startSlider.max = windowMax;
        endSlider.min = windowMin;
        endSlider.max = windowMax;
        
        // Definir valores iniciais
        startSlider.value = initialStart;
        endSlider.value = initialEnd;
        
        // Estado do slider
        let isDragging = false;
        let lastHandle = null;
        let debounceTimer = null;
        
        // Atualizar interface
        function updateUI() {
            const startSec = parseFloat(startSlider.value);
            const endSec = parseFloat(endSlider.value);
            
            // Garantir que fim > início com gap mínimo
            const minGap = 0.5;
            if (endSec <= startSec + minGap) {
                if (lastHandle === 'start') {
                    endSlider.value = startSec + minGap;
                } else {
                    startSlider.value = endSec - minGap;
                }
            }
            
            const finalStart = parseFloat(startSlider.value);
            const finalEnd = parseFloat(endSlider.value);
            
            // Atualizar barra visual
            const startPercent = ((finalStart - windowMin) / windowRange) * 100;
            const endPercent = ((finalEnd - windowMin) / windowRange) * 100;
            
            sliderRange.style.left = `${startPercent}%`;
            sliderRange.style.width = `${endPercent - startPercent}%`;
            
            // Atualizar labels
            startLabel.textContent = `Início: ${secondsToTimestamp(finalStart)}`;
            endLabel.textContent = `Fim: ${secondsToTimestamp(finalEnd)}`;
            
            const duration = finalEnd - finalStart;
            const minutes = Math.floor(duration / 60);
            const seconds = Math.floor(duration % 60);
            durationLabel.textContent = `Duração: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Função de preview
        function handlePreview(isStart) {
            const startSec = parseFloat(startSlider.value);
            const endSec = parseFloat(endSlider.value);
            const previewVideo = document.getElementById(`preview-${clipId}`);
            
            if (!previewVideo) {
                console.warn(`[PREVIEW] Vídeo preview-${clipId} não encontrado`);
                return;
            }
            
            let seekTime;
            if (isStart) {
                seekTime = startSec;
            } else {
                // Para fim: tocar 6s antes, mas não antes do início
                seekTime = Math.max(startSec, endSec - 1);
            }
            
            console.log(`[PREVIEW] Clip ${clipId} - Buscando tempo: ${seekTime}s (isStart: ${isStart})`);
            
            // Pausar outros vídeos
            document.querySelectorAll('.video-preview-thumbnail').forEach(video => {
                if (video !== previewVideo && !video.paused) {
                    video.pause();
                }
            });
            
            // Função para aplicar o seekTime quando o vídeo estiver pronto
            const applySeekTime = () => {
                console.log(`[PREVIEW] Aplicando seekTime ${seekTime}s ao vídeo (readyState: ${previewVideo.readyState})`);
                previewVideo.currentTime = seekTime;
                previewVideo.muted = false;
                
                const playPromise = previewVideo.play();
                if (playPromise !== undefined) {
                    playPromise.catch(err => {
                        console.warn('Falha ao tocar preview:', err);
                        previewVideo.muted = true;
                        previewVideo.play();
                    });
                }
            };
            
            // Se o vídeo já tem dados suficientes, aplica imediatamente
            if (previewVideo.readyState >= 2) {
                applySeekTime();
            } else {
                // Aguarda o vídeo carregar dados suficientes
                const onCanPlay = () => {
                    previewVideo.removeEventListener('canplay', onCanPlay);
                    applySeekTime();
                };
                previewVideo.addEventListener('canplay', onCanPlay);
                
                // Força o carregamento se necessário
                if (previewVideo.readyState === 0) {
                    previewVideo.load();
                }
            }
        }
        
        // Event listeners
        startSlider.addEventListener('input', () => {
            lastHandle = 'start';
            updateUI();
        });
        
        endSlider.addEventListener('input', () => {
            lastHandle = 'end';
            updateUI();
        });
        
        startSlider.addEventListener('mousedown', () => {
            isDragging = true;
            startSlider.classList.add('updating');
        });
        
        endSlider.addEventListener('mousedown', () => {
            isDragging = true;
            endSlider.classList.add('updating');
        });
        
        // Eventos de fim de arraste
        function handleMouseUp() {
            if (isDragging) {
                isDragging = false;
                startSlider.classList.remove('updating');
                endSlider.classList.remove('updating');
                
                // Trigger preview e persistência
                if (lastHandle === 'start') {
                    handlePreview(true);
                } else if (lastHandle === 'end') {
                    handlePreview(false);
                }
                
                persistChanges();
            }
        }
        
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('touchend', handleMouseUp);
        
        // Suporte a teclado
        function handleKeyDown(e) {
            const step = e.shiftKey ? 1 : (e.ctrlKey ? 5 : 0.1);
            let changed = false;
            
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                if (e.target === startSlider) {
                    startSlider.value = Math.max(windowMin, parseFloat(startSlider.value) - step);
                    lastHandle = 'start';
                } else {
                    endSlider.value = Math.max(windowMin, parseFloat(endSlider.value) - step);
                    lastHandle = 'end';
                }
                changed = true;
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                if (e.target === startSlider) {
                    startSlider.value = Math.min(windowMax, parseFloat(startSlider.value) + step);
                    lastHandle = 'start';
                } else {
                    endSlider.value = Math.min(windowMax, parseFloat(endSlider.value) + step);
                    lastHandle = 'end';
                }
                changed = true;
            }
            
            if (changed) {
                updateUI();
                persistChanges();
            }
        }
        
        startSlider.addEventListener('keydown', handleKeyDown);
        endSlider.addEventListener('keydown', handleKeyDown);
        
        // Inicializar UI
        updateUI();
    }

    // Gera estilos CSS de crop 9:16 baseado em parametrosCorte e dimensões do vídeo
    function generateVideoStyles(parametrosCorte, videoElement) {
        if (!parametrosCorte) return '';

        const xCenter = parseInt(parametrosCorte.x_center);
        const yCenter = parseInt(parametrosCorte.y_center);
        const cropWidth = parseInt(parametrosCorte.width);
        const cropHeight = parseInt(parametrosCorte.height);

        // Dimensões do vídeo original - detecta dinamicamente se possível
        let videoWidth = 1920; // padrão
        let videoHeight = 1080; // padrão

        if (videoElement && videoElement.videoWidth && videoElement.videoHeight) {
            videoWidth = videoElement.videoWidth;
            videoHeight = videoElement.videoHeight;
        }

        // Calcula as coordenadas do canto superior esquerdo (x1, y1)
        let x1 = xCenter - Math.floor(cropWidth / 2);
        let y1 = yCenter - Math.floor(cropHeight / 2);

        // Garante que o retângulo fique dentro dos limites
        if (x1 < 0) x1 = 0;
        if ((x1 + cropWidth) > videoWidth) x1 = videoWidth - cropWidth;
        if (y1 < 0) y1 = 0;
        if ((y1 + cropHeight) > videoHeight) y1 = videoHeight - cropHeight;

        // Retorna estilos inline para aplicar no elemento <video>
        return `
            object-fit: cover;
            object-position: ${x1}px ${y1}px;
            width: 100%;
            height: 100%;
        `;
    }

    // Função para aplicar redimensionamento aos vídeos após serem criados
    function applyVideoCropping(parametrosCorte) {
        if (!parametrosCorte) return;

        const videos = document.querySelectorAll('.video-preview-thumbnail');
        videos.forEach(video => {
            // Adicionar classe para estilos CSS
            video.classList.add('cropped');
            
            // Aplicar estilos inline para o crop
            const styles = generateVideoStyles(parametrosCorte, video);
            if (styles) {
                video.style.cssText = styles;
            }
        });
    }

    // Função para converter timestamp SRT (00:01:15.280) para segundos
    function timestampToSeconds(timestamp) {
        if (!timestamp || typeof timestamp !== 'string') {
            console.error('[ERROR] Timestamp inválido:', timestamp);
            return 0;
        }
        
        try {
            const parts = timestamp.split(':');
            if (parts.length !== 3) {
                console.error('[ERROR] Formato de timestamp inválido:', timestamp);
                return 0;
            }
            
            const hours = parseInt(parts[0]) || 0;
            const minutes = parseInt(parts[1]) || 0;
            const secondsParts = parts[2].split('.');
            const seconds = parseInt(secondsParts[0]) || 0;
            // Corrigir: milliseconds podem ter 3 dígitos, não apenas 1
            const milliseconds = parseInt((secondsParts[1] || '0').padEnd(3, '0')) || 0;
            
            const totalSeconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000;
            
            console.log(`[DEBUG] Conversão timestamp: ${timestamp} → ${totalSeconds}s`);
            return totalSeconds;
        } catch (error) {
            console.error('[ERROR] Erro ao converter timestamp:', timestamp, error);
            return 0;
        }
    }

    // Função para converter segundos para timestamp SRT (00:01:15.280)
    function secondsToTimestamp(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        const milliseconds = Math.floor((seconds % 1) * 1000);
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
    }

    // Função para configurar controles de preview dos vídeos
    function setupVideoPreviewControls() {
        document.querySelectorAll('.play-preview-btn').forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const videoElement = document.getElementById(targetId);
                const startTime = timestampToSeconds(videoElement.getAttribute('data-start'));
                const endTime = timestampToSeconds(videoElement.getAttribute('data-end'));
                
                playVideoSegment(videoElement, startTime, endTime, this);
            });
        });
    }

    // Validação simples de timestamp no formato hh:mm:ss.mmm
    function isValidTimestamp(ts) {
        return /^\d{2}:\d{2}:\d{2}\.\d{3}$/.test(ts);
    }

    // Calcula duração entre dois timestamps e retorna em formato legível
    function calculateDuration(startTimestamp, endTimestamp) {
        const startSeconds = timestampToSeconds(startTimestamp);
        const endSeconds = timestampToSeconds(endTimestamp);
        const durationSeconds = endSeconds - startSeconds;
        
        const minutes = Math.floor(durationSeconds / 60);
        const seconds = Math.floor(durationSeconds % 60);
        
        if (minutes > 0) {
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else {
            return `00:${seconds.toString().padStart(2, '0')}`;
        }
    }

    // Função para tocar um segmento específico do vídeo
    function playVideoSegment(videoElement, startTime, endTime, buttonElement) {
        const playIcon = '<i class="fas fa-play"></i> Preview';
        const pauseIcon = '<i class="fas fa-pause"></i> Pausar';
        
        if (videoElement.paused) {
            // Para todos os outros vídeos que possam estar tocando
            document.querySelectorAll('.video-preview-thumbnail').forEach(video => {
                if (video !== videoElement && !video.paused) {
                    video.pause();
                }
            });
            
            // Define o tempo inicial e toca
            videoElement.currentTime = startTime;
            try {
                videoElement.muted = false;
                videoElement.volume = 1.0;
                const playPromise = videoElement.play();
                if (playPromise !== undefined) {
                    playPromise.catch(err => {
                        console.warn('Falha ao iniciar reprodução com áudio:', err);
                        // Como fallback, tentar tocar sem áudio e informar usuário
                        videoElement.muted = true;
                        videoElement.play();
                    });
                }
            } catch (e) {
                console.warn('Erro ao tocar segmento:', e);
            }
            buttonElement.innerHTML = pauseIcon;
            
            // Monitora o tempo para parar no final do segmento
            const timeUpdateHandler = function() {
                if (videoElement.currentTime >= endTime) {
                    videoElement.pause();
                    buttonElement.innerHTML = playIcon;
                    videoElement.removeEventListener('timeupdate', timeUpdateHandler);
                }
            };
            
            videoElement.addEventListener('timeupdate', timeUpdateHandler);
            
            // Handler para quando o vídeo é pausado manualmente
            const pauseHandler = function() {
                buttonElement.innerHTML = playIcon;
                videoElement.removeEventListener('timeupdate', timeUpdateHandler);
                videoElement.removeEventListener('pause', pauseHandler);
            };
            
            videoElement.addEventListener('pause', pauseHandler);
            
        } else {
            // Pausa o vídeo
            videoElement.pause();
            buttonElement.innerHTML = playIcon;
        }
    }

    

    // Função para configurar event listeners dos botões de geração de vídeo
    function setupGenerateVideoButtons() {
        document.querySelectorAll('.generate-video-btn').forEach(button => {
            button.addEventListener('click', async function() {
                try {
                    // Obter dados do trecho selecionado
                    const startTime = this.getAttribute('data-start');
                    const endTime = this.getAttribute('data-end');
                    const title = this.getAttribute('data-title');
                    const clipId = this.getAttribute('clip_id');
                    
                    console.log('Trecho selecionado:', { startTime, endTime, title, clipId });
                    
                    // Verificar se temos um arquivo na sessão
                    if (!currentFilename) {
                        throw new Error('Nenhum arquivo de vídeo encontrado na sessão');
                    }
                    
                    // Preparar dados do trecho
                    const trechoData = {
                        filename: currentFilename,
                        start_time: startTime,
                        end_time: endTime,
                        title: title || 'Vídeo gerado automaticamente',
                        clip_id: clipId
                    };
                    
                    // Mostrar loading no botão
                    const originalText = this.innerHTML;
                    this.disabled = true;
                    this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processando...';
                    
                    console.log('Enviando dados do trecho para processamento:', trechoData);
                    
                    // Enviar dados do trecho para /process-clip
                    const response = await fetch('/process-clip', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(trechoData)
                    });
                    
                    const responseData = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(responseData.message || 'Erro ao processar o vídeo');
                    }
                    
                    // Sucesso! Vídeo processado
                    console.log('Vídeo processado com sucesso:', responseData);
                    
                    if (responseData.status === 'success' && responseData.video_url) {
                        // Trocar o preview pelo vídeo processado nas mesmas dimensões
                        const previewVideo = document.getElementById(`preview-${clipId}`);
                        
                        if (previewVideo) {
                            // Manter as mesmas dimensões e estilos
                            const currentStyles = previewVideo.style.cssText;
                            const currentClasses = previewVideo.className;
                            
                            // Atualizar o src para o vídeo processado
                            previewVideo.src = responseData.video_url;
                            
                            // Manter os estilos e classes
                            previewVideo.style.cssText = currentStyles;
                            previewVideo.className = currentClasses;
                            
                            // Remover atributos de tempo já que agora é o vídeo final
                            previewVideo.removeAttribute('data-start');
                            previewVideo.removeAttribute('data-end');
                            
                            // Atualizar o botão de preview para indicar que é o vídeo final
                            const playButton = document.querySelector(`[data-target="preview-${clipId}"]`);
                            if (playButton) {
                                playButton.innerHTML = '<i class="fas fa-play"></i> Vídeo Final';
                            }
                            
                            console.log('Preview trocado pelo vídeo processado:', responseData.video_url);
                        }
                        
                        // Atualizar o botão para indicar sucesso
                        this.innerHTML = '<i class="fas fa-check"></i> Vídeo Processado';
                        this.classList.remove('btn-success');
                        this.classList.add('btn-primary');
                        
                        // Mostrar mensagem de sucesso
                        showSuccess(`Vídeo "${title}" processado com sucesso!`);
                        
                    } else {
                        throw new Error('Resposta inválida do servidor');
                    }
                    
                } catch (error) {
                    console.error('Erro ao processar vídeo:', error);
                    showError(`Erro ao processar vídeo: ${error.message}`);
                    
                    // Restaurar botão em caso de erro
                    this.disabled = false;
                    this.innerHTML = originalText;
                }
            });
        });
    }

    // Função para começar um novo projeto
    async function startNewProject() {
        try {
            // Limpa a sessão no backend
            const response = await fetch('/clear-session', { 
                method: 'POST', 
                credentials: 'include' 
            });
            
            if (response.ok) {
                // Reseta a UI
                uploadForm.reset();
                currentFilename = '';
                videoPreviewOriginal.src = '';
                transcriptionText.value = '';
                hideError();
                showSection(uploadSection);
                transcriptionDisplay.classList.add('d-none');
                actionsSection.classList.add('d-none');
                document.getElementById('viral-clips-section').classList.add('d-none');
                document.getElementById('viral-clips-container').innerHTML = '';
                
                // Mostra mensagem de sucesso
                showSuccess('Projeto limpo com sucesso! Você pode começar um novo projeto.');
                
                // Esconde a mensagem após 3 segundos
                setTimeout(() => {
                    hideSuccess();
                }, 3000);
            } else {
                throw new Error('Falha ao limpar a sessão no servidor');
            }
        } catch (error) {
            console.error('Erro ao limpar a sessão:', error);
            showError('Erro ao limpar o projeto. Tente novamente.');
        }
    }

    // Função para reiniciar a aplicação (limpa a sessão no backend)
    window.resetApp = async function() {
        try {
            // Limpa a sessão no backend
            await fetch('/clear-session', { method: 'POST', credentials: 'include' });
        } catch (error) {
            console.error('Erro ao limpar a sessão:', error);
        }

        // Reseta a UI
        uploadForm.reset();
        currentFilename = '';
        videoPreviewOriginal.src = '';
        transcriptionText.value = '';
        hideError();
        showSection(uploadSection);
        transcriptionDisplay.classList.add('d-none');
        actionsSection.classList.add('d-none');
        document.getElementById('viral-clips-section').classList.add('d-none');
        document.getElementById('viral-clips-container').innerHTML = '';
        
        // Recarrega a página para garantir que a sessão seja limpa visualmente
        window.location.reload();
    }
});
