import os
import threading
import cv2
import requests
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from ultralytics import YOLO
from vidgear.gears import CamGear
import statistics
from moviepy.editor import VideoFileClip

app = Flask(__name__)

# Configuração da autenticação Twilio
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

whatsapp_number = input("Digite o numero de telefone (DD e NUMERO): ")

twilio_number = 'whatsapp:+14155238886'  
# alterar o "55" se for usar um telefone de outro país
to_number = "whatsapp:+55" + whatsapp_number

# Carregar o modelo YOLOv8 globalmente
model = YOLO('yolov8n-seg.pt')

@app.route('/bot', methods=['POST'])
def bot():
    media_url = request.form.get('MediaUrl0')
    message_sid = request.form.get('MessageSid')
    body = request.form.get('Body')
    from_number = request.form.get('From') 

    if media_url and message_sid:
        reply = MessagingResponse()
        reply.message("Processando vídeo...")
        
        threading.Thread(target=process_video_and_reply, args=(media_url, from_number)).start()
        
        return str(reply)
    elif body and body.startswith('https://www.youtube.com/watch'):
        reply = MessagingResponse()
        reply.message("Processando vídeo...")
        
        threading.Thread(target=process_youtube_video, args=(body, from_number)).start()
        
        return str(reply)
    else:
        reply = MessagingResponse()
        reply.message("Por favor, envie um link do YouTube para que eu possa identificar o conteúdo.")
        return str(reply)

def process_video_and_reply(media_url, from_number):
    try:
        # Fazer o download do vídeo enviado
        video_response = requests.get(media_url)
        video_filename = "received_video.mp4"
        with open(video_filename, 'wb') as f:
            f.write(video_response.content)
        print(f"Vídeo baixado com sucesso: {video_filename}")

        # Identificar o tipo de arquivo de vídeo e converter para mp4 se necessário
        clip = VideoFileClip(video_filename)
        converted_filename = "converted_video.mp4"
        clip.write_videofile(converted_filename, codec='libx264')
        print(f"Vídeo convertido para MP4: {converted_filename}")

        # Processar o vídeo convertido
        process_video(converted_filename, from_number)
    
    except Exception as e:
        print(f"Erro ao processar vídeo do WhatsApp: {e}")

def process_youtube_video(youtube_url, from_number):
    print(f"Recebido URL do YouTube: {youtube_url}")  

    try:
        stream = CamGear(source=youtube_url, stream_mode=True, logging=True).start()
    except Exception as e:
        print(f"Erro ao iniciar o stream: {e}")  
        return

    desired_width = 1920
    desired_height = 1080

    identified_objects = {}
    frame_count = 0 

    while True:
        frame = stream.read()

        if frame is None:
            break

        frame_count += 1
        print(f"Processando quadro {frame_count}...")  

        resized_frame = cv2.resize(frame, (desired_width, desired_height))

        try:
            results = model(resized_frame)
            print(f"Resultados: {results}")  
        except Exception as e:
            print(f"Erro na inferência: {e}")  
            continue


        for result in results:
            try:
                boxes = result.boxes 
                for box in boxes:
                    class_id = int(box.cls[0]) 
                    confidence = box.conf[0] 
                    class_name = model.names[class_id]

                    if class_name not in identified_objects:
                        identified_objects[class_name] = []

                    identified_objects[class_name].append(confidence)
            except AttributeError as e:
                print(f"Erro ao processar resultados: {e}")  


    stream.stop()

    print("Processamento concluído.") 


    response = []
    for class_name, confidences in identified_objects.items():
        avg_conf = sum(confidences) / len(confidences)
        med_conf = statistics.median(confidences)
        response.append(f"{class_name}: count={len(confidences)}, avg={avg_conf:.2f}, median={med_conf:.2f}")

    response_text = "Objetos identificados:\n" + "\n".join(response)
    print(response_text)  

    try:
        message = client.messages.create(
            body=response_text,
            from_=twilio_number,
            to=from_number
        )
        print(f"Mensagem enviada com sucesso! SID: {message.sid}")  
    except Exception as e:
        print(f"Erro ao enviar a mensagem: {e}")  

def process_video(video_filename, from_number):
    print(f"Processando vídeo: {video_filename}")  

    identified_objects = {}

    cap = cv2.VideoCapture(video_filename)

    frame_count = 0 

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1
        print(f"Processando quadro {frame_count}...")  

        try:
            results = model(frame)
            print(f"Resultados: {results}")  
        except Exception as e:
            print(f"Erro na inferência: {e}")  
            continue


        for result in results:
            try:
                boxes = result.boxes 
                for box in boxes:
                    class_id = int(box.cls[0]) 
                    confidence = box.conf[0] 
                    class_name = model.names[class_id]

                    if class_name not in identified_objects:
                        identified_objects[class_name] = []

                    identified_objects[class_name].append(confidence)
            except AttributeError as e:
                print(f"Erro ao processar resultados: {e}")  


    cap.release()
    print("Processamento de vídeo concluído.") 
    send_identification_results(identified_objects, from_number)

def send_identification_results(identified_objects, from_number):
    response = []
    for class_name, confidences in identified_objects.items():
        avg_conf = sum(confidences) / len(confidences)
        med_conf = statistics.median(confidences)
        response.append(f"{class_name}: count={len(confidences)}, avg={avg_conf:.2f}, median={med_conf:.2f}")

    response_text = "Objetos identificados:\n" + "\n".join(response)
    print(response_text)  

    try:
        message = client.messages.create(
            body=response_text,
            from_=twilio_number,
            to=from_number
        )
        print(f"Mensagem enviada com sucesso! SID: {message.sid}")  
    except Exception as e:
        print(f"Erro ao enviar a mensagem: {e}")  

if __name__ == '__main__':
    app.run(debug=True)
