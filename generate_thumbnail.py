
"""
            # use o opencv e pegue o primeiro frame do short
            import cv2
            cap = cv2.VideoCapture(result_path)
            _, frame = cap.read()
            cap.release()

            import google.generativeai as genai
            from PIL import Image
            from io import BytesIO
            
            
            prompt = f'''
            A partir da imagem enviada, crie uma imagem realista em 9:16 
            onde a ação pode ser baseada na descrição delimitada por <desc>. 
            Os únicos textos que deve conter a imagem estão delimitador por <titulo>.
            <titulo>{clip_encontrado['titulo_sugestivo']}</titulo> 
            <desc>{clip_encontrado['descricao_para_postagem']}</desc>
            ''' 
            
            # Converter de BGR (cv2) para RGB e depois para PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            load_dotenv()
            api_key = os.getenv('GEMINI_API_KEY')

            # Configura o cliente Gemini
            genai.configure(api_key=api_key)
            
            # Configuração para garantir que a saída seja JSON
            generation_config = genai.GenerationConfig(response_mime_type="application/json")

            # Cria o modelo
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-image-preview',
                generation_config=generation_config,
                contents=[prompt, image]
            )

            response = model.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt, image],
            )
            
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    
                    image = Image.open(BytesIO(part.inline_data.data))   
                    #redimencioane a imagem usando parametros_corte
                    image = image.resize((parametros_corte['width'], parametros_corte['height']))
                    image.save("generated_image.png")

                    # Adicionar a imagem ao primeiro frame do short
                    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
                    
                    # Carregar o vídeo original
                    video = VideoFileClip(result_path)
                    
                    # Criar clip da imagem gerada
                    image_clip = ImageClip("generated_image.png")
                    image_clip = image_clip.set_duration(video.duration)
                    image_clip = image_clip.set_position('center')
                    
                    # Compor o vídeo final com a imagem sobreposta
                    final_video = CompositeVideoClip([video, image_clip])
                    
                    # Salvar o vídeo final
                    final_output_path = result_path.replace('.mp4', '_with_image.mp4')
                    final_video.write_videofile(final_output_path, codec='libx264', audio_codec='aac')
                    
                    # Fechar os clips para liberar memória
                    video.close()
                    image_clip.close()
                    final_video.close()
"""