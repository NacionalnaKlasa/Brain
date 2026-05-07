import time
import board
import neopixel

from .config import (
    SIGNAL_LIGHT_FRONT_RIGHT_ID, SIGNAL_LIGHT_FRONT_LEFT_ID,
    SIGNAL_LIGHT_REAR_RIGHT_ID,  SIGNAL_LIGHT_REAR_LEFT_ID,
    LIGHT_FRONT_ID, LIGHT_REAR_ID,
    LIGHT_Enum,
)

# ── Colors (RGB — library handles GRB reordering internally) ──────────
AMBER = (255, 165,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
OFF   = (  0,   0,   0)

# ── Blinker timing ────────────────────────────────────────────────────
BLINKER_STEP_MS = 70    # ms between each LED lighting up sequentially
BLINKER_OFF_MS  = 400   # ms pause (all dark) before next sweep


class WS2812:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(
            board.D18, 60,
            brightness=0.2, auto_write=False, pixel_order=neopixel.GRB
        )

        self._lightFrontOn = True
        self._lightRearOn  = True
        self._lightLeftOn  = True
        self._lightRightOn = True

        # Blinker animation state per side.
        # frame == 0  →  pause (all dark, wait BLINKER_OFF_MS)
        # frame == N  →  N LEDs lit sequentially
        self._left_frame  = 0
        self._right_frame = 0
        self._left_t      = time.monotonic()
        self._right_t     = time.monotonic()

        self._max_left  = max(len(SIGNAL_LIGHT_FRONT_LEFT_ID),
                              len(SIGNAL_LIGHT_REAR_LEFT_ID))
        self._max_right = max(len(SIGNAL_LIGHT_FRONT_RIGHT_ID),
                              len(SIGNAL_LIGHT_REAR_RIGHT_ID))

    # ── Public API ────────────────────────────────────────────────────

    def turnOn(self, light: LIGHT_Enum = LIGHT_Enum.NONE):
        if light == LIGHT_Enum.FRONT: self._lightFrontOn = True
        elif light == LIGHT_Enum.REAR:  self._lightRearOn  = True
        elif light == LIGHT_Enum.LEFT:  self._lightLeftOn  = True
        elif light == LIGHT_Enum.RIGHT: self._lightRightOn = True

    def turnOff(self, light: LIGHT_Enum = LIGHT_Enum.NONE):
        if light == LIGHT_Enum.FRONT: self._lightFrontOn = False
        elif light == LIGHT_Enum.REAR:  self._lightRearOn  = False
        elif light == LIGHT_Enum.LEFT:  self._lightLeftOn  = False
        elif light == LIGHT_Enum.RIGHT: self._lightRightOn = False

    def tick(self):
        """Call once per thread iteration to update all LED outputs."""
        now = time.monotonic()

        # ── Steady front lights (white) ───────────────────────────────
        for idx in LIGHT_FRONT_ID:
            self.pixels[idx] = WHITE if self._lightFrontOn else OFF

        # ── Steady rear lights (red) ──────────────────────────────────
        for idx in LIGHT_REAR_ID:
            self.pixels[idx] = RED if self._lightRearOn else OFF

        # ── Left blinker ──────────────────────────────────────────────
        if self._lightLeftOn:
            self._left_frame, self._left_t = self._advance(
                self._left_frame, self._left_t, now, self._max_left
            )
            self._draw_blinker(SIGNAL_LIGHT_FRONT_LEFT_ID, self._left_frame)
            self._draw_blinker(SIGNAL_LIGHT_REAR_LEFT_ID,  self._left_frame)
        else:
            self._left_frame = 0
            for idx in SIGNAL_LIGHT_FRONT_LEFT_ID + SIGNAL_LIGHT_REAR_LEFT_ID:
                self.pixels[idx] = OFF

        # ── Right blinker ─────────────────────────────────────────────
        if self._lightRightOn:
            self._right_frame, self._right_t = self._advance(
                self._right_frame, self._right_t, now, self._max_right
            )
            self._draw_blinker(SIGNAL_LIGHT_FRONT_RIGHT_ID, self._right_frame)
            self._draw_blinker(SIGNAL_LIGHT_REAR_RIGHT_ID,  self._right_frame)
        else:
            self._right_frame = 0
            for idx in SIGNAL_LIGHT_FRONT_RIGHT_ID + SIGNAL_LIGHT_REAR_RIGHT_ID:
                self.pixels[idx] = OFF

        self.pixels.show()

    # ── Internal helpers ──────────────────────────────────────────────

    def _advance(self, frame, last_t, now, max_leds):
        """Advance blinker state machine. Returns (new_frame, new_t)."""
        elapsed_ms = (now - last_t) * 1000
        if frame == 0:
            # Pause phase — wait before starting next sweep
            if elapsed_ms >= BLINKER_OFF_MS:
                return 1, now
        else:
            # Sweep phase — light one more LED every BLINKER_STEP_MS
            if elapsed_ms >= BLINKER_STEP_MS:
                next_frame = frame + 1
                if next_frame > max_leds:
                    return 0, now   # All lit → back to pause
                return next_frame, now
        return frame, last_t

    def _draw_blinker(self, led_ids, frame):
        """Light the first `frame` LEDs in led_ids amber, rest off."""
        for i, idx in enumerate(led_ids):
            self.pixels[idx] = AMBER if i < frame else OFF
