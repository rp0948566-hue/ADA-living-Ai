def send_whatsapp_tool(message, recipient):
    print(f"Tool: Sending WhatsApp: {message} to {recipient}")
    return True

def generate_whatsapp_message_tool(context, recipient):
    return f"Tool generated message for {recipient}: {context}"

def get_whatsapp_info_tool():
    return "WhatsApp info retrieved"

WHATSAPP_TOOLS = [send_whatsapp_tool, generate_whatsapp_message_tool, get_whatsapp_info_tool]
