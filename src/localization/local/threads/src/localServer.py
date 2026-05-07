import socket
import json


class LocalServer:
    """
    TCP client that connects to PC's PCServer and streams position updates.
    Reuses the same JSON-lines protocol as the rest of the Floyd TCP stack.
    """

    def __init__(self, ip: str, port: int):
        self._ip   = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connected   = False
        self._initialized = False
        self._buffer      = ""

    def start(self) -> bool:
        """Connect and wait for the PC's {"type": "init"} handshake."""
        try:
            self._sock.connect((self._ip, self._port))
            self._sock.setblocking(False)
            self._connected = True
            print(f"[LocalServer] Connected to PC {self._ip}:{self._port}")
        except Exception as e:
            print(f"[LocalServer] Connection failed: {e}")
            return False

        # Wait for init (blocking poll)
        import time
        import select
        deadline = time.time() + 5.0
        while time.time() < deadline:
            r, _, _ = select.select([self._sock], [], [], 0.1)
            if r:
                for msg in self._read_messages():
                    if msg.get("type") == "init":
                        self._initialized = True
                        print("[LocalServer] PC init received — ready.")
                        return True
        print("[LocalServer] Timeout waiting for init.")
        return False

    def send_position(self, x: float, y: float, angle_rad: float):
        if not self._connected:
            return
        self._send({"type": "position", "x": x, "y": y, "angle": angle_rad})

    def send_checkpoint(self, name: str):
        if not self._connected:
            return
        self._send({"type": "checkpoint", "name": name})

    def send_lane_snap(self):
        if not self._connected:
            return
        self._send({"type": "lane"})

    def send_nav_command(self, command: str):
        if not self._connected:
            return
        self._send({"type": "nav", "command": command})

    def send_telemetry(self, speed: float, steer: float):
        if not self._connected:
            return
        self._send({"type": "telemetry", "speed": speed, "steering_angle": steer})

    def close(self):
        try:
            self._sock.close()
        except Exception:
            pass

    # ── Internal ──────────────────────────────────────────────────────

    def _send(self, data: dict):
        try:
            self._sock.sendall((json.dumps(data) + "\n").encode("utf-8"))
        except Exception:
            pass

    def _read_messages(self):
        try:
            chunk = self._sock.recv(1024).decode("utf-8")
            self._buffer += chunk
        except BlockingIOError:
            pass
        except Exception:
            pass
        messages = []
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return messages
