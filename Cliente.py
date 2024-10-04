import zmq
import threading

def recibir_mensajes(socket):
    while True:
        try:
            partes = socket.recv_multipart()
            if len(partes) >= 3:
                identidad_origen, _, mensaje = partes[0], partes[1], partes[2]
                print(f"Mensaje recibido de {identidad_origen.decode('utf-8')}: {mensaje.decode('utf-8')}")
            else:
                print("Error: El mensaje recibido tiene un formato inesperado.")
        except Exception as e:
            print(f"Error al recibir el mensaje: {e}")
            break

def cliente():
    identidad_cliente = f"cliente-{hash(threading.current_thread()) % 1000000}"
    print(f"Conectado con identidad: {identidad_cliente}")

    contexto = zmq.Context()
    socket = contexto.socket(zmq.DEALER)
    socket.setsockopt_string(zmq.IDENTITY, identidad_cliente)

    # Conectar al servidor
    socket.connect("tcp://0.tcp.ngrok.io:10401")  # Cambia la dirección según sea necesario

    # Iniciar un hilo para recibir mensajes
    threading.Thread(target=recibir_mensajes, args=(socket,), daemon=True).start()

    while True:
        try:
            mensaje = input("Introduce el mensaje ('enviar <id_cliente> <mensaje>' para enviar a uno, 'todos <mensaje>' para enviar a todos): ")

            # Validar el formato del mensaje
            if mensaje.startswith('enviar') or mensaje.startswith('todos'):
                # Enviar mensaje en formato multipart
                socket.send_multipart([identidad_cliente.encode('utf-8'), b"", mensaje.encode('utf-8')])
            else:
                print("Error: Formato incorrecto. Usa 'enviar <id_cliente> <mensaje>' o 'todos <mensaje>'")

        except KeyboardInterrupt:
            print("Desconectando...")
            break
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")

if __name__ == "__main__":
    cliente()
