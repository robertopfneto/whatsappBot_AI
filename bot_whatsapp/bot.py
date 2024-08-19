import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import threading
import cv2
from ultralytics import YOLO
from vidgear.gears import CamGear
import pandas as pd
import statistics

app = Flask(__name__)

# Configuração da autenticação Twilio
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

# Número do Twilio (WhatsApp)
twilio_number = 'whatsapp:+14155238886'  # Número de envio via WhatsApp
# Número do destinatário
to_number = 'whatsapp:+556791416568'  # Número de destino

# Carregar o modelo YOLOv8 globalmente
model = YOLO('yolov8n-seg.pt')

@app.route('/bot', methods=['POST'])
def bot():
    media_url = request.form.get('MediaUrl0')
    message_sid = request.form.get('MessageSid')
    body = request.form.get('Body')
    from_number = request.form.get('From')  # Número do remetente

    if media_url and message_sid:
        # Enviar a resposta inicial de "Carregando"
        reply = MessagingResponse()
        reply.message("Carregando... por favor, aguarde.")
        
        # Processar o vídeo em uma thread separada
        threading.Thread(target=process_video_and_reply, args=(from_number,)).start()
        
        return str(reply)
    elif body and body.startswith('https://www.youtube.com/watch'):
        # Enviar a resposta inicial de "Carregando"
        reply = MessagingResponse()
        reply.message("Carregando... por favor, aguarde.")
        
        # Processar o vídeo do YouTube em uma thread separada
        threading.Thread(target=process_youtube_video, args=(body,)).start()
        
        return str(reply)
    else:
        reply = MessagingResponse()
        reply.message("Por favor, envie um link do YouTube para que eu possa identificar o conteúdo.")
        return str(reply)

def process_video_and_reply(from_number):
    # Aqui você implementa a lógica para processar o vídeo que foi recebido via Twilio
    print(f"Processando vídeo para o número: {from_number}")
    # Adicione a lógica para baixar, processar o vídeo e enviar a resposta ao usuário

def process_youtube_video(youtube_url):
    print(f"Recebido URL do YouTube: {youtube_url}")  # Log

    # Inicializar o stream do vídeo
    try:
        stream = CamGear(source=youtube_url, stream_mode=True, logging=True).start()
    except Exception as e:
        print(f"Erro ao iniciar o stream: {e}")  # Log
        return

    # Resolução desejada
    desired_width = 1920
    desired_height = 1080

    identified_objects = {}
    frame_count = 0  # Contador de quadros

    while True:
        frame = stream.read()

        if frame is None:
            break

        frame_count += 1
        print(f"Processando quadro {frame_count}...")  # Log

        # Redimensionar o quadro para a resolução desejada
        resized_frame = cv2.resize(frame, (desired_width, desired_height))

        # Fazer a inferência
        try:
            results = model(resized_frame)
            print(f"Resultados: {results}")  # Log
        except Exception as e:
            print(f"Erro na inferência: {e}")  # Log
            continue

        # Extrair as informações dos resultados
        for result in results:
            try:
                boxes = result.boxes  # Obter as caixas delimitadoras
                for box in boxes:
                    class_id = int(box.cls[0])  # Obter o ID da classe
                    confidence = box.conf[0]  # Obter a confiança
                    class_name = model.names[class_id]

                    if class_name not in identified_objects:
                        identified_objects[class_name] = []

                    identified_objects[class_name].append(confidence)
            except AttributeError as e:
                print(f"Erro ao processar resultados: {e}")  # Log

    # Limpar
    stream.stop()

    print("Processamento concluído.")  # Log

    # Formatar a resposta
    response = []
    for class_name, confidences in identified_objects.items():
        avg_conf = sum(confidences) / len(confidences)
        med_conf = statistics.median(confidences)
        response.append(f"{class_name}: count={len(confidences)}, avg={avg_conf:.2f}, median={med_conf:.2f}")

    response_text = "Objetos identificados:\n" + "\n".join(response)
    print(response_text)  # Log

    # Enviar a mensagem para o número do destinatário via WhatsApp
    try:
        message = client.messages.create(
            body=response_text,
            from_=twilio_number,
            to=to_number
        )
        print(f"Mensagem enviada com sucesso! SID: {message.sid}")  # Log
    except Exception as e:
        print(f"Erro ao enviar a mensagem: {e}")  # Log

if __name__ == '__main__':
    app.run(debug=True)
