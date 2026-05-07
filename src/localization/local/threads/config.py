from pathlib import Path

# ── TCP connection to PC ──────────────────────────────────────────────
SERVER_IP   = "192.168.50.101"   # PC IP — change if needed
SERVER_PORT = 65432

# ── Track geometry (competition track) ───────────────────────────────
WORLD_SIZE_X      = 20.648   # physical track width  [m]
WORLD_SIZE_Y      = 13.798   # physical track height [m]
GRAPH_COORD_SPACE = 20.648   # must equal WORLD_SIZE_X
FLIP_Y            = True     # graph Y is math-convention (up)

# Virtual screen dimensions used by LaneSnapper coordinate space.
# These do NOT need a real display — they just define the pixel/meter scale.
VIRTUAL_WIDTH  = 1700
VIRTUAL_HEIGHT = round(VIRTUAL_WIDTH * WORLD_SIZE_Y / WORLD_SIZE_X)  # 1136

SCREEN_SCALE = VIRTUAL_WIDTH / WORLD_SIZE_X   # px/m  (≈ 82.33)

# ── Car start position ────────────────────────────────────────────────
CAR_START_X   = 2.0    # [m]
CAR_START_Y   = 2.0    # [m]
CAR_START_ANG = 0      # [deg]

# ── Graph file ────────────────────────────────────────────────────────
# Relative to Floyd project root (3 levels up from this file).
# Override with an absolute path if the project lives elsewhere on RPi.
_ROOT      = Path(__file__).resolve().parents[2]
GRAPH_FILE = str(_ROOT / "local" / "Competition_track_graph.graphml")

# ── Steer / speed mapping (mirrors main.py) ───────────────────────────
STEER_OFFSET         = 1.6
STEER_MAX_POS        = 226
STEER_MAX_NEG        = 196
STEER_LIMIT          = 25.0   # degrees
STEER_HYSTERESIS_DEG = 2.5
