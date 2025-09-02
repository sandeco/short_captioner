@app.route('/caption', methods=['POST'])
def caption_video():
    print("=== ENDPOINT /caption CHAMADO ===")
    data = request.get_json()
    print(f"Dados recebidos: {data}")
    if not data or 'filename' not in data or 'phrases' not in data:
        print("Erro: Dados incompletos")
        return jsonify({'status': 'error', 'message': 'Dados incompletos para legendagem'}), 400

    filename = data['filename']
    phrases = data['phrases']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    print(f"Verificando arquivo de vídeo: {video_path}")
    if not os.path.exists(video_path):
        print(f"Arquivo não encontrado: {video_path}")
        return jsonify({'status': 'error', 'message': 'Arquivo de vídeo não encontrado'}), 404
    
    print(f"Arquivo encontrado: {video_path}")
    print(f"Tamanho do arquivo: {os.path.getsize(video_path)} bytes")
    
    captioner = None
    try:
        output_filename = f"captioned_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        print(f"Caminho de saída: {output_path}")
        
        # Processa as frases para o formato esperado pela classe ShortCaptioner
        processed_phrases = []
        for phrase in phrases:
            # Calcula a duração da frase
            duration = phrase['end'] - phrase['start']
            processed_phrases.append({
                'text': phrase['text'],
                'start': phrase['start'],
                'end': phrase['end'],
                'duration': duration
            })
        
        print(f"Frases processadas: {processed_phrases}")
        
        # Instancia sua classe ShortCaptioner
        print("Instanciando ShortCaptioner...")
        captioner = ShortCaptioner(
            video_path=video_path,
            font_path="GothamBlack.ttf",
            font_size=70,
            font_color="yellow",
            stroke_color="black",
            stroke_width=3,
            position=("center", "bottom"),
            margin_bottom=700
        )
        
        print("ShortCaptioner instanciado com sucesso")
        
        # Chama o método sem karaoke
        print("Chamando create_captioned_video_from_phrases...")
        captioner.create_captioned_video_from_phrases(processed_phrases, output_path)
        
        print(f"Vídeo gerado com sucesso: {output_path}")
        final_video_url = url_for('download_file', filename=output_filename)
        print(f"URL do vídeo final: {final_video_url}")
        
        return jsonify({'status': 'success', 'video_url': final_video_url})
    
    except Exception as e:
        print(f"Erro na legendagem: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        # Garante que o arquivo de vídeo original seja fechado
        if captioner and hasattr(captioner, 'video') and captioner.video:
            captioner.video.close()
