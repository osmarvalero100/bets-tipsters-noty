import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
import requests

load_dotenv()  # Carga variables del archivo .env

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
FILTER_PHRASE = os.getenv('FILTER_PHRASE').split(',')
BOT_FATHER_TOKEN = os.getenv('BOT_FATHER_TOKEN')
GROUP_ID_BY_NOTY = int(os.getenv('GROUP_ID_BY_NOTY'))
TIPSTERS_CHANNELS = [int(channel_id) for channel_id in os.getenv('TIPSTERS_CHANNELS').split(',')]

# Ruta para el archivo de sesión (en el directorio actual)
SESSION_FILE = 'user_session'
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

async def send_photo(photo_bytes, caption):
    """Envía una imagen al grupo de destino usando la API de Telegram"""
    url = f'https://api.telegram.org/bot{BOT_FATHER_TOKEN}/sendPhoto'
    
    # Preparar los datos para la solicitud multipart/form-data
    files = {
        'photo': ('photo.jpg', photo_bytes, 'image/jpeg')
    }
    
    data = {
        'chat_id': GROUP_ID_BY_NOTY,
        'caption': caption,
        'parse_mode': 'Markdown'
    }
    
    # Usar asyncio.to_thread para ejecutar la solicitud HTTP de manera asíncrona
    await asyncio.to_thread(
        lambda: requests.post(url, files=files, data=data)
    )
    
    return True

@client.on(events.NewMessage(chats=TIPSTERS_CHANNELS))
async def handler(event):
    try:
        message = event.message
        resend = False
        
        if message.message is not None:
            for phrase in FILTER_PHRASE:
                if phrase.lower() in message.message.lower() and 'https://t.me/+' not in message.message.lower() and 'https://shops.kunfupay' not in message.message.lower():  # Corregido: el orden de comprobación
                    resend = True
                    break
                
        if resend:
            # Preparar el texto del mensaje
            source_text = f"_Fuente: {message.chat.title}_"
            # Si hay media (imagen)
            if message.media is not None:
                try:
                    # Descargar la imagen como bytes
                    photo_bytes = await message.download_media(bytes)
                    # Crear un mensaje con el texto original (si existe)
                    caption = f"🚨 **Free Bet**\n\n{message.message}\n\n{source_text}" if message.message else f"🚨 **Free Bet**\n\n{source_text}"
                    
                    # Enviar la imagen con el texto como caption
                    await send_photo(photo_bytes, caption)
                    print(f"Imagen reenviada del canal: {message.chat.title}")
                except Exception as e:
                    print(f"Error al reenviar imagen: {str(e)}")
            
            # Si hay texto y no se ha enviado junto con una imagen
            elif message.message and len(message.message) > 0:
                url = f'https://api.telegram.org/bot{BOT_FATHER_TOKEN}/sendMessage'
                text = f"🚨 **Free Bet**\n\n{message.message}\n\n{source_text}"
                requests.post(url, data={'chat_id': GROUP_ID_BY_NOTY, 'text': text, 'parse_mode': 'Markdown'})
                print(f"Mensaje reenviado: {message.message}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

async def main():
    await client.start()
    print("Escuchando mensajes... (Presiona Ctrl+C para detener)")
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDetenido por el usuario")
