def send_whatsapp_message(message, recipient):
    print(f"Sending WhatsApp message: {message} to {recipient}")
    return True

class WhatsAppSender:
    def __init__(self):
        print("WhatsAppSender initialized")

    def send(self, message, recipient):
        print(f"WhatsAppSender sending: {message} to {recipient}")
        return True
