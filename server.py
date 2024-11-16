from flask import Flask, request, send_file
import tempfile
import os
import shutil
import soundfile as sf
from spleeter.separator import Separator

app = Flask(__name__)

# Создаем временный каталог для хранения файлов
temp_dir = tempfile.mkdtemp()

@app.route('/separate', methods=['POST'])
def separate():
    # Получаем файл из запроса
    file = request.files['audio']
    
    if not file:
        return "Ошибка: не удалось получить аудиофайл", 400
    
    # Сохраняем файл во временной директории
    temp_path = os.path.join(temp_dir, 'input.wav')
    file.save(temp_path)
    
    try:
        # Загружаем модель Spleeter
        separator = Separator('spleeter:2stems')
        
        # Разделяем трек на голос и музыку
        output_path = temp_dir
        filename = os.path.splitext(os.path.basename(file.filename))[0]
        separator.separate_to_file(temp_path, output_path, filename=filename)
        
        vocal_path = f"{output_path}/{filename}_vocals.wav"
        music_path = f"{output_path}/{filename}_accompaniment.wav"
        
        with open(vocal_path, 'rb') as fp:
            response_vocals = send_file(fp, mimetype='audio/wav')
            
        with open(music_path, 'rb') as mp:
            response_music = send_file(mp, mimetype='audio/wav')
        
        return {
            'vocal': response_vocals,
            'music': response_music
        }
    
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return f"Ошибка: {str(e)}", 500
    
if __name__ == '__main__':
    app.run(debug=True)
