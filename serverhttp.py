import asyncio          # Para programación asíncrona (WebSocket)
import websockets       # Para el servidor WebSocket
from http.server import SimpleHTTPRequestHandler, HTTPServer  # Para servidor HTTP
import threading        # Para ejecutar dos servidores al mismo tiempo

# Configuración
ip = "192.168.0.11"
port = 8765          # Puerto para WebSocket
# Puerto 8000 para HTTP (definido más abajo)

# Lista global de clientes WebSocket conectados
CLIENTS = set()

async def notify_all(message):
    """
    Envía un mensaje a TODOS los clientes WebSocket conectados
    Esta función es asíncrona porque puede enviar a muchos clientes
    """
    # list(CLIENTS) = crear copia para evitar errores si se desconectan
    for ws in list(CLIENTS):
        try:
            await ws.send(message)   # Enviar mensaje al cliente
        except Exception:            # Si falla (cliente desconectado)
            CLIENTS.discard(ws)      # Remover de la lista

async def ws_handler(websocket):
    """
    Función que maneja cada conexión WebSocket
    Se ejecuta UNA VEZ por cada cliente que se conecta
    """
    # 1️⃣ Cliente se conecta - OBTENER INFORMACIÓN DEL CLIENTE
    CLIENTS.add(websocket)
    
    # 🆕 Obtener IP y puerto del cliente
    client_ip = websocket.remote_address[0]      # IP del cliente
    client_port = websocket.remote_address[1]    # Puerto del cliente
    client_info = f"{client_ip}:{client_port}"   # Formato "IP:Puerto"
    
    print(f"Cliente conectado desde {client_info}. Total: {len(CLIENTS)}")
    
    # 🆕 Notificar a todos que un usuario se conectó
    join_message = f"🟢 Usuario {client_info} se ha unido al chat"
    await notify_all(join_message)
    
    try:
        # 2️⃣ Escuchar mensajes infinitamente
        async for message in websocket:
            print(f"Mensaje de {client_info}: {message}")
            
            # 3️⃣ Formatear mensaje con información del remitente
            formatted_message = f"[{client_info}] {message}"
            
            # 4️⃣ Reenviar mensaje formateado a todos los clientes
            await notify_all(formatted_message)
    finally:
        # 5️⃣ Cliente se desconecta (por cualquier razón)
        CLIENTS.discard(websocket)
        print(f"Cliente {client_info} desconectado. Total: {len(CLIENTS)}")
        
        # 🆕 Notificar a todos que un usuario se desconectó
        leave_message = f"🔴 Usuario {client_info} ha salido del chat"
        await notify_all(leave_message)

async def ws_main():
    """
    Función principal del servidor WebSocket
    Crea el servidor y lo mantiene corriendo
    """
    async with websockets.serve(ws_handler, ip, port):
        print(f"Servidor WebSocket en ws://{ip}:{port}")
        await asyncio.Future()  # Mantener corriendo para siempre

def run_http():
    """
    Función que ejecuta el servidor HTTP
    Este servidor sirve archivos estáticos (HTML, CSS, JS, imágenes)
    """
    # HTTPServer = crear servidor HTTP
    # SimpleHTTPRequestHandler = maneja requests automáticamente
    server = HTTPServer((ip, 8000), SimpleHTTPRequestHandler)
    print(f"Servidor HTTP en http://{ip}:8000")
    server.serve_forever()  # Mantener corriendo para siempre

if __name__ == "__main__":
    # 🔹 THREADING: Ejecutar dos cosas al mismo tiempo
    # Crear hilo para servidor HTTP
    # daemon=True = si el programa principal termina, este hilo también
    threading.Thread(target=run_http, daemon=True).start()
    
    # 🔹 ASYNCIO: Ejecutar servidor WebSocket
    # Esta línea bloquea el programa principal
    asyncio.run(ws_main())