import os, socket, threading, json
from states import motor_info_state

SOCK_PATH = "/tmp/intbus.sock"

def run_motor_info_server(stop_event: threading.Event,
                      on_message=None,
                      sock_path: str = SOCK_PATH,
                      period: float = 0.5):
    """
    Tiny Unix-domain socket server that accepts JSON-encoded dicts.
    - stop_event: threading.Event to stop the loop
    - on_message: callable(dict) called when a dict arrives
    - period: accept() timeout in seconds
    """
    try: os.unlink(sock_path)
    except FileNotFoundError: pass

    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        srv.bind(sock_path)
        os.chmod(sock_path, 0o666)
        srv.listen(1)
        srv.settimeout(period)
        print(f"[server] listening on {sock_path}")

        while not stop_event.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            try:
                data = conn.recv(4096)
                if data:
                    try:
                        msg = json.loads(data.decode())
                        if on_message:
                            motor_info_state['delay'] = msg['delay']
                            motor_info_state['spr'] = msg['spr']
                            motor_info_state['angles_per_step'] = 360 / msg['spr']
                            
                            on_message(msg)
                        else:
                            print("[server] got dict:", msg)
                    except json.JSONDecodeError:
                        print("[server] invalid JSON:", data)
            finally:
                conn.close()
    finally:
        srv.close()
        try: os.unlink(sock_path)
        except FileNotFoundError: pass
        print("[server] stopped")
