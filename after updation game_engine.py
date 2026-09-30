import math
import random
import pygame


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None

        self.stamina = 100.0
        self.max_stamina = 100.0

        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35

        # ============================================================
        # AI SURGE SYSTEM
        # ============================================================
        self.ai_state = "BUILDING"
        self.ai_energy = 0.0
        self.ai_max_energy = 100.0

        # Energy builds gradually until a power surge is triggered.
        self.ai_energy_gain_rate = 25.0

        # Power surge lasts approximately 1.5 seconds.
        self.ai_surge_duration = 1.5
        self.ai_surge_timer = 0.0

        # AI becomes exhausted after the surge.
        self.ai_exhausted_duration = 2.5
        self.ai_exhausted_timer = 0.0

        # AI recovery period before returning to building.
        self.ai_recovery_duration = 2.0
        self.ai_recovery_timer = 0.0

        # Force multipliers for different AI states.
        self.ai_surge_multiplier = 2.0
        self.ai_exhausted_multiplier = 0.45

        # Used to calculate frame-rate-independent elapsed time.
        self._last_update_time = pygame.time.get_ticks() / 1000.0

        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:

            # Player cannot push when exhausted.
            if self.stamina <= 10:
                return

            # ========================================================
            # TASK 1: PLAYER PUSH DIRECTION FIX
            # ========================================================
            # Player input must move arm_position toward the
            # negative winning threshold (-100).
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT:
                    self.arm_position -= 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_LEFT

            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT:
                    self.arm_position -= 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_RIGHT

    def update(self):
        if self.game_state != "PLAYING":
            return

        # ============================================================
        # FRAME-RATE-INDEPENDENT TIMING
        # ============================================================
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - self._last_update_time
        self._last_update_time = current_time

        # Protect against unusually large time jumps.
        dt = min(dt, 0.1)

        # ============================================================
        # TASK 2: DYNAMIC AI SURGE / DIFFICULTY SYSTEM
        # ============================================================

        if self.ai_state == "BUILDING":
            # Gradually build AI energy.
            self.ai_energy = min(
                self.ai_max_energy,
                self.ai_energy + self.ai_energy_gain_rate * dt
            )

            # Trigger power surge once energy is full.
            if self.ai_energy >= self.ai_max_energy:
                self.ai_state = "SURGE"
                self.ai_surge_timer = self.ai_surge_duration
                self.ai_energy = 0.0

        elif self.ai_state == "SURGE":
            # Countdown the surge using real elapsed time.
            self.ai_surge_timer -= dt

            if self.ai_surge_timer <= 0:
                self.ai_state = "EXHAUSTED"
                self.ai_exhausted_timer = self.ai_exhausted_duration

        elif self.ai_state == "EXHAUSTED":
            # AI is temporarily weak after using its surge.
            self.ai_exhausted_timer -= dt

            if self.ai_exhausted_timer <= 0:
                self.ai_state = "RECOVERING"
                self.ai_recovery_timer = self.ai_recovery_duration

        elif self.ai_state == "RECOVERING":
            # Short recovery period before rebuilding energy.
            self.ai_recovery_timer -= dt

            if self.ai_recovery_timer <= 0:
                self.ai_state = "BUILDING"
                self.ai_energy = 0.0

        # ------------------------------------------------------------
        # Determine AI force based on its current state.
        # ------------------------------------------------------------
        ai_variance = random.uniform(0.3, 1.0)

        if self.ai_state == "SURGE":
            ai_multiplier = self.ai_surge_multiplier

        elif self.ai_state == "EXHAUSTED":
            ai_multiplier = self.ai_exhausted_multiplier

        elif self.ai_state == "RECOVERING":
            ai_multiplier = 0.75

        else:
            # BUILDING / normal behavior.
            ai_multiplier = 1.0

        # The original AI moved approximately
        # ai_strength * ai_variance per frame at 60 FPS.
        #
        # Multiplying by 60 * dt preserves approximately the same
        # behavior while making the movement frame-rate independent.
        ai_force = (
            self.ai_strength
            * ai_variance
            * ai_multiplier
            * 60.0
            * dt
        )

        self.arm_position += ai_force

        # ============================================================
        # PLAYER STAMINA RECOVERY
        # ============================================================
        if self.stamina < self.max_stamina:
            self.stamina = min(
                self.max_stamina,
                self.stamina + 0.8 * 60.0 * dt
            )

        # ============================================================
        # WIN / LOSS DETECTION
        # ============================================================
        if self.arm_position <= -self.target_limit:
            self.arm_position = -self.target_limit
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"

        elif self.arm_position >= self.target_limit:
            self.arm_position = self.target_limit
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        # ============================================================
        # RESET AI SURGE SYSTEM
        # ============================================================
        self.ai_state = "BUILDING"
        self.ai_energy = 0.0
        self.ai_surge_timer = 0.0
        self.ai_exhausted_timer = 0.0
        self.ai_recovery_timer = 0.0

        self._last_update_time = pygame.time.get_ticks() / 1000.0

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render(
            "ARM WRESTLE SHOWDOWN",
            True,
            (240, 240, 240)
        )
        screen.blit(
            title_surf,
            (self.width // 2 - title_surf.get_width() // 2, 12)
        )

        player_header = self.font_med.render(
            "PLAYER",
            True,
            (80, 160, 255)
        )

        computer_header = self.font_med.render(
            "COMPUTER",
            True,
            (255, 100, 80)
        )

        screen.blit(player_header, (60, 55))
        screen.blit(
            computer_header,
            (self.width - 150, 55)
        )

        # ============================================================
        # TABLE
        # ============================================================
        table_rect = pygame.Rect(
            40,
            100,
            self.width - 80,
            310
        )

        pygame.draw.rect(
            screen,
            (110, 50, 15),
            table_rect,
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            (70, 30, 8),
            table_rect,
            width=5,
            border_radius=14
        )

        pygame.draw.line(
            screen,
            (45, 18, 4),
            (self.width // 2, 100),
            (self.width // 2, 410),
            4
        )

        # ============================================================
        # ARM POSITION
        # ============================================================
        offset_x = (
            self.arm_position / self.target_limit
        ) * 95

        hand_x = (
            self.width // 2
        ) + int(offset_x)

        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)

        c_shoulder = (
            self.width - 70,
            330
        )

        c_elbow = (
            self.width - 140,
            215
        )

        # Player arm
        pygame.draw.line(
            screen,
            (200, 145, 110),
            p_shoulder,
            p_elbow,
            32
        )

        pygame.draw.line(
            screen,
            (215, 160, 125),
            p_elbow,
            (hand_x, hand_y),
            26
        )

        pygame.draw.circle(
            screen,
            (185, 130, 95),
            p_elbow,
            18
        )

        # Computer arm
        pygame.draw.line(
            screen,
            (170, 110, 85),
            c_shoulder,
            c_elbow,
            32
        )

        pygame.draw.line(
            screen,
            (185, 125, 95),
            c_elbow,
            (hand_x, hand_y),
            26
        )

        pygame.draw.circle(
            screen,
            (150, 95, 70),
            c_elbow,
            18
        )

        # Hands
        pygame.draw.circle(
            screen,
            (225, 175, 140),
            (hand_x, hand_y),
            24
        )

        pygame.draw.circle(
            screen,
            (160, 115, 85),
            (hand_x, hand_y),
            24,
            width=3
        )

        # ============================================================
        # STAMINA
        # ============================================================
        stamina_label = self.font_med.render(
            "STAMINA",
            True,
            (220, 220, 220)
        )

        screen.blit(
            stamina_label,
            (40, 445)
        )

        stamina_bg = pygame.Rect(
            140,
            448,
            240,
            22
        )

        stamina_fill = pygame.Rect(
            140,
            448,
            int(
                240 * (
                    self.stamina /
                    self.max_stamina
                )
            ),
            22
        )

        pygame.draw.rect(
            screen,
            (45, 50, 60),
            stamina_bg,
            border_radius=6
        )

        # ============================================================
        # TASK 3 + TASK 4: EXHAUSTION WARNING
        # ============================================================
        if self.stamina <= 10:
            # Flash approximately twice per second.
            flash_on = (
                pygame.time.get_ticks() // 250
            ) % 2 == 0

            if flash_on:
                bar_color = (255, 40, 40)
            else:
                bar_color = (150, 30, 30)
        else:
            bar_color = (
                (60, 210, 100)
                if self.stamina > 25
                else (220, 60, 60)
            )

        pygame.draw.rect(
            screen,
            bar_color,
            stamina_fill,
            border_radius=6
        )

        # Display exhaustion warning.
        if self.stamina <= 10:
            exhausted_surf = self.font_med.render(
                "EXHAUSTED!",
                True,
                (255, 70, 70)
            )

            screen.blit(
                exhausted_surf,
                (
                    400,
                    445
                )
            )

        # ============================================================
        # AI STATE INDICATOR
        # ============================================================
        ai_state_text = {
            "BUILDING": "AI: BUILDING",
            "SURGE": "AI: POWER SURGE!",
            "EXHAUSTED": "AI: EXHAUSTED",
            "RECOVERING": "AI: RECOVERING"
        }

        ai_text = ai_state_text.get(
            self.ai_state,
            "AI: READY"
        )

        if self.ai_state == "SURGE":
            ai_color = (255, 180, 50)
        elif self.ai_state == "EXHAUSTED":
            ai_color = (120, 180, 255)
        else:
            ai_color = (200, 200, 200)

        ai_status_surf = self.font_med.render(
            ai_text,
            True,
            ai_color
        )

        screen.blit(
            ai_status_surf,
            (
                self.width - ai_status_surf.get_width() - 40,
                445
            )
        )

        # ============================================================
        # GAME OVER SCREEN
        # ============================================================
        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 200)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            win_text = (
                "PLAYER WINS THE MATCH!"
                if self.winner == "PLAYER"
                else "COMPUTER WINS!"
            )

            color = (
                (80, 240, 100)
                if self.winner == "PLAYER"
                else (240, 80, 80)
            )

            text_surf = self.font_big.render(
                win_text,
                True,
                color
            )

            screen.blit(
                text_surf,
                (
                    self.width // 2
                    - text_surf.get_width() // 2,
                    self.height // 2 - 45
                )
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch",
                True,
                (240, 240, 240)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2
                    - restart_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )
