# LLM-Assisted Development Flow

ORIGINAL GAME
↓
Run + observe
↓
10-second BEFORE video
↓
PROMPT 1
↓
LLM analyzes existing code
↓
Critical code review
↓
IMPLEMENTATION PROMPT
↓
Apply changes
↓
Run game
↓
TESTING PROMPT
↓
Verify requirements
↓
10-second AFTER video
↓
Submit complete ChatGPT conversation link














I am a gamer using LLM-assisted vibe coding to improve and enhance the Arm Wrestle Showdown game.

Project:
Arm Wrestle Showdown — a Pygame-based tug-of-war/arm-wrestling game.

Repository:
https://github.com/SETAPESU26/53_arm_wrestle

I have already downloaded and run the original project successfully. I have also observed the original behavior before making any changes.

I will now provide the COMPLETE contents of:
game/game_engine.py

Your job is to act as my AI pair-programming partner.

IMPORTANT:
- Do NOT immediately rewrite the entire file.
- Do NOT change unrelated functionality.
- Do NOT introduce unnecessary libraries or dependencies.
- Preserve the existing class structure, game loop, rendering style, controls, win/loss logic, stamina mechanics, and restart behavior unless a change is required for the tasks.
- Work incrementally and explain your reasoning before modifying code.
- I will critically review your suggestions before applying them.

The assignment has these requirements:

TASK 1 — Fix inverted arm push bug
The player wins when arm_position reaches the negative target threshold:
arm_position <= -self.target_limit

Currently, when the player correctly alternates Left Arrow and Right Arrow, the input handler adds +4.2 to arm_position instead of subtracting it.

Fix the sign so successful player inputs move arm_position toward the player's negative winning threshold.

TASK 2 — Dynamic AI surge / difficulty spikes
Currently, the AI applies force at a mostly constant average rate using:
self.ai_strength * ai_variance

Modify the AI behavior inside game_engine.update() so that:

1. The AI normally operates at its existing/base strength.
2. The AI gradually builds up an internal energy/stamina value.
3. Periodically, the AI enters a POWER SURGE state.
4. During the POWER SURGE, AI force becomes temporarily stronger than normal.
5. The surge must last approximately 1–2 seconds.
6. After the surge ends, the AI enters an EXHAUSTED state.
7. During AI exhaustion, its resistance/force must temporarily become weaker than normal.
8. The AI should then recover and return to its normal state.
9. The behavior should create a dynamic back-and-forth rhythm rather than simply making the AI permanently stronger.
10. Avoid making the game unfair or impossible for the player.
11. Use delta time or the existing timing mechanism appropriately so the behavior is frame-rate independent.

TASK 3 — Player exhaustion warning
The player currently cannot provide input when stamina falls below 10.

Add clear visual feedback whenever:

self.stamina < 10

The warning should make it immediately obvious to the player that input has been disabled because of exhaustion.

Use a visually clear implementation such as:
- flashing/pulsing stamina bar,
- "EXHAUSTED!" text,
- or another appropriate visual effect.

Prefer a simple, clean implementation that matches the existing game's visual style.

TASK 4 — Duplicate requirement
The README lists Task 4 as another exhaustion warning indicator and it duplicates Task 3.

Do NOT create an unnecessary second exhaustion system.

Instead, implement one polished exhaustion-warning system that satisfies both Task 3 and Task 4.

EXPECTED BEHAVIOR:
- Alternating Left and Right Arrow presses move the player's arm toward the negative side.
- Player movement can eventually reach approximately -100 and win.
- AI movement can reach approximately +100 and cause a computer win.
- Rapid player input drains stamina.
- When stamina falls below 10, player input is disabled.
- The exhaustion warning is visible while stamina is below 10.
- AI periodically performs a stronger power surge lasting about 1–2 seconds.
- AI becomes temporarily exhausted/weaker after its surge.
- AI eventually recovers.
- Pressing R on the Game Over screen resets the game correctly.
- Existing gameplay and rendering should remain intact.

FIRST RESPONSE REQUIREMENT:

Before writing any modified code, analyze the supplied game_engine.py and provide:

1. A short architecture overview.
2. The exact location/function responsible for Task 1.
3. The existing AI force logic and where Task 2 should be implemented.
4. The existing stamina/input logic and where Task 3 should be implemented.
5. The rendering function(s) where the exhaustion warning should be drawn.
6. Any important existing variables that should be reused.
7. A minimal implementation plan broken into small steps.
8. Potential risks or unintended side effects we should watch for.

Do not modify code yet.

Wait for my approval before producing the implementation.








This is the game_engine.py you have to make changes....



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

        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if self.stamina <= 10:
                return

            # BUG SYMPTOM:
            # Adding to arm_position pushes it toward the COMPUTER
            # instead of reducing it to win.
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT:
                    self.arm_position += 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_LEFT

            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT:
                    self.arm_position += 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_RIGHT

    def update(self):
        if self.game_state != "PLAYING":
            return

        ai_variance = random.uniform(0.3, 1.0)
        self.arm_position += self.ai_strength * ai_variance

        if self.stamina < self.max_stamina:
            self.stamina = min(
                self.max_stamina,
                self.stamina + 0.8
            )

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"

        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render(
            "ARM WRESTLE SHOWDOWN",
            True,
            (240, 240, 240)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2
                - title_surf.get_width() // 2,
                12
            )
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

        screen.blit(
            player_header,
            (60, 55)
        )

        screen.blit(
            computer_header,
            (self.width - 150, 55)
        )

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

        offset_x = (
            self.arm_position
            / self.target_limit
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
                240
                * (
                    self.stamina
                    / self.max_stamina
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






after the updated code given by the llm.

I have reviewed your analysis and approve the implementation plan.

Now implement the changes incrementally.

IMPORTANT IMPLEMENTATION RULES:

1. Modify only the necessary portions of game_engine.py.
2. Preserve the existing architecture and naming conventions where practical.
3. Do not rewrite unrelated functions.
4. Do not remove existing functionality.
5. Do not add external dependencies.

IMPLEMENTATION ORDER:

STEP 1:
Fix the Task 1 input-direction bug.

The player's alternating input must move:
arm_position → negative direction

and eventually allow:
arm_position <= -self.target_limit

STEP 2:
Implement the AI surge system.

Use explicit AI states or an equivalent clean mechanism, for example:

NORMAL
BUILDING
SURGE
EXHAUSTED
RECOVERING

The exact implementation should fit the existing code.

Requirements:
- normal AI behavior remains close to the original.
- energy gradually builds.
- surge occurs periodically.
- surge duration approximately 1–2 seconds.
- AI force increases during surge.
- AI force decreases during exhaustion.
- AI recovers afterward.
- timing should be frame-rate independent.
- avoid abrupt or unfair permanent difficulty increases.

STEP 3:
Implement the player exhaustion warning.

When:
self.stamina < 10

show a clear visual warning.

Prefer:
- "EXHAUSTED!" text
- plus a flashing/pulsing stamina bar if this can be added cleanly.

The existing stamina mechanics must remain intact.

STEP 4:
Ensure the existing game-over and R restart behavior still works.

STEP 5:
Review the entire modified file for:
- syntax errors
- undefined variables
- incorrect state transitions
- timing errors
- rendering errors
- incorrect sign/direction
- accidental changes to existing mechanics.

OUTPUT FORMAT:

First provide:
A. Summary of changes
B. Variables added/modified
C. Functions changed
D. How each task is satisfied
E. Testing procedure

Then provide:
F. The complete modified game_engine.py

Clearly mark the important new sections with concise comments such as:

# Player push direction fix
# AI surge system
# Player exhaustion warning

Do not hide any changes.






Prompt for testing....


I have implemented your changes and run the game.

Now help me perform a structured verification of the assignment.

Create a test checklist for:

1. Original bug fixed
2. Player movement direction
3. Player stamina depletion
4. Player exhaustion at stamina < 10
5. Exhaustion warning visibility
6. AI normal behavior
7. AI power surge activation
8. AI surge duration of approximately 1–2 seconds
9. AI post-surge exhaustion
10. AI recovery
11. Player win at approximately -100
12. Computer win at approximately +100
13. R restart behavior
14. No regression in existing rendering/gameplay

For every test, specify:
- Action to perform
- Expected result
- What I should observe on screen
- Whether the test passes or fails

Also tell me which tests are best to demonstrate in my 10-second AFTER video.








