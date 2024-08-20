import statistics
from twilio_client import get_twilio_client

twilio_number = 'whatsapp:+14155238886'

def send_identification_results(identified_objects, from_number):
    response = []
    for class_name, confidences in identified_objects.items():
        avg_conf = sum(confidences) / len(confidences)
        med_conf = statistics.median(confidences)
        response.append(f"{class_name}: count={len(confidences)}, avg={avg_conf:.2f}, median={med_conf:.2f}")

    response_text = "Identified objects:\n" + "\n".join(response)
    print(response_text)  

    try:
        client = get_twilio_client()
        message = client.messages.create(
            body=response_text,
            from_=twilio_number,
            to=from_number
        )
        print(f"Message sent successfully! SID: {message.sid}")  
    except Exception as e:
        print(f"Error sending message: {e}")  
