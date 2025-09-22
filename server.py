import asyncio
import websockets

ip = "192.168.0.11"
port = 8765

# Lista para mantener clientes conectados
clients = set()

async def handler(websocket):
    """
    Funcion que maneja cada cliente que se conecta
    se ejecuta una vez por cada navegador que se conecta
    y permanece activa hasta que el cliente se desconecta
    """
    # Conexion: agregar cliente a la lista
    clients.add(websocket)
    print(f"Cliente conectado. Total: {len(clients)}")
    
    try:
        # Escuchar mensajes del cliente: con un loop infinito esperamos mensajes
        async for msg in websocket:
            print(f"Mensaje recibido: {msg}")

            # re-enviar mensaje a todos los clientes conectados
            for client in clients.copy(): # copy es para evitar errores si se desconecta un cliente
                try:
                    await client.send(msg) # envio mensaje a cada cliente
                except websockets.exceptions.ConnectionClosed:
                    clients.remove(client) # si falla, lo elimino
    except websockets.exceptions.ConnectionClosed:
        # Cliente se desconecto normalmente
        pass
    finally:
        # Remover cliente cuando se desconecta
        clients.discard(websocket)
        print(f"Cliente desconectado. Total: {len(clients)}")

async def main():
    async with websockets.serve(handler, ip, port):
        print(f"Servidor de chat escuchando en ws://{ip}:{port}")
        await asyncio.Future() # mantener el servidor corriendo

if __name__ == "__main__":
    asyncio.run(main())