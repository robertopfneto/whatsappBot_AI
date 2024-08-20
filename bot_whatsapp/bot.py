from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import threading
from download_video import process_whatsapp_video, process_youtube_video, clean_videos_directory

app = Flask(__name__)

numero = input("Digite seu numero de whatsapp (DD e Numero sem espaços): ")

twilio_number = 'whatsapp:+14155238886' 
to_number = 'whatsapp:+55'+numero 

@app.route('/bot', methods=['POST'])
def bot():
    print("Request received.") 
    media_url = request.form.get('MediaUrl0')
    body = request.form.get('Body')
    from_number = request.form.get('From')  
    print(f"From: {from_number}, Media URL: {media_url}, Body: {body}")  

    reply = MessagingResponse()
    
    clean_videos_directory()
    
    if media_url:
        reply.message("Processing video...")
        threading.Thread(target=process_whatsapp_video, args=(media_url, from_number)).start()
        
    elif body and body.startswith('https://www.youtube.com/watch'):
        reply.message("Processing YouTube video...")
        threading.Thread(target=process_youtube_video, args=(body, from_number)).start()
    
    else:
        reply.message("Please send a video for processing and object identification.")
    
    return str(reply)

if __name__ == '__main__':
    app.run(debug=True)
