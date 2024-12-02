import asyncio
import websockets

connected_clients = {}  # Dictionary untuk menyimpan client dan labelnya
client_counter = 1      # Counter untuk memberi nomor pada setiap client

async def handler(websocket, path):
    global client_counter

    client_label = f"Client {client_counter}"  # Buat label dengan nomor
    connected_clients[websocket] = client_label  # Simpan label untuk setiap client
    client_counter += 1                          # Increment counter

    print(f"{client_label} connected")

    try:
        # Kirim pesan sambutan ke client
        await websocket.send(f"Welcome, {client_label}!")

        async for message in websocket:
            print(f"{client_label}: {message}")

            # Broadcast ke semua client lain
            for client, label in connected_clients.items():
                if client != websocket:  # Kirim ke client lain, kecuali pengirim
                    await client.send(f"{client_label}: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"{client_label} disconnected")
    finally:
        # Hapus client dari daftar saat terputus
        del connected_clients[websocket]

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8080):  # Bind ke IPv4 saja
        print("WebSocket server is running on ws://127.0.0.1:8080")
        await asyncio.Future()  # Run forever

asyncio.run(main())
