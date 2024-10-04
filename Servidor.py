import zmq
import threading

# Diccionario para almacenar clientes conectados
clientes_conectados = {}

def servidor():
    contexto = zmq.Context()
    socket = contexto.socket(zmq.ROUTER)  # Usar ROUTER para manejar múltiples clientes
    socket.bind("tcp://*:6665")  # Escuchar en el puerto 5556

    print("Servidor iniciado y esperando conexiones...")

    while True:
        try:
            # Recibir mensaje multipart
            partes = socket.recv_multipart()

            # Mostrar todas las partes recibidas para depuración
           # print(f"Partes recibidas (sin procesar): {[p.decode('utf-8') for p in partes]}")

            if len(partes) >= 3:
                identidad_cliente = partes[0]  # Identidad del cliente
                mensaje = partes[3].decode('utf-8')  # Mensaje recibido, que es la cuarta parte

                # Registrar el cliente en el diccionario si no está ya registrado
                cliente_id = identidad_cliente.decode('utf-8')
                if cliente_id not in clientes_conectados:
                    clientes_conectados[cliente_id] = identidad_cliente
                    print(f"Cliente {cliente_id} conectado.")

                print(f"Mensaje recibido de {cliente_id}: {mensaje}")

                # Procesar el mensaje
                if mensaje.startswith('todos '):
                    contenido = mensaje[6:]  # Eliminar 'todos ' y extraer el contenido
                    print(f"Mensaje para todos: {contenido}")

                    # Reenviar el mensaje a todos los clientes conectados
                    for cliente, identidad in clientes_conectados.items():
                        socket.send_multipart([identidad, b"", contenido.encode('utf-8')])

                elif mensaje.startswith('enviar '):
                    partes_mensaje = mensaje.split(" ", 2)
                    if len(partes_mensaje) == 3:
                        _, id_destino, contenido = partes_mensaje
                        if id_destino in clientes_conectados:  # Validar si el cliente existe
                            print(f"Reenviando mensaje a {id_destino}: {contenido}")
                            socket.send_multipart([clientes_conectados[id_destino], b"", contenido.encode('utf-8')])
                        else:
                            print(f"Error: El cliente {id_destino} no está conectado.")
                            # Enviar mensaje de error al cliente que intenta enviar
                            socket.send_multipart([identidad_cliente, b"", f"Error: El cliente {id_destino} no está conectado.".encode('utf-8')])
                    else:
                        print("Error: El mensaje de envío no tiene el formato correcto.")
                else:
                    print("Comando no reconocido.")
            else:
                print("Error: El mensaje recibido tiene un formato inesperado.")
        except Exception as e:
            print(f"Error en el servidor: {e}")
            break

if __name__ == "__main__":
    servidor()
