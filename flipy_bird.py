import tkinter as tk
import random
import os
import math

class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird")
        self.root.resizable(False, False)
        
        # Center the window on screen
        self.width = 480
        self.height = 640
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_pos = (screen_width // 2) - (self.width // 2)
        y_pos = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x_pos}+{y_pos}")
        
        # Game canvas with standard Flappy sky blue
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#70c5cf", highlightthickness=0)
        self.canvas.pack()
        
        # Bind keyboard controls
        self.root.bind("<space>", self.jump)
        self.root.bind("<Up>", self.jump)
        self.root.bind("<r>", self.restart_event)
        self.root.bind("<R>", self.restart_event)
        
        # Load high score
        self.highscore_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".flappy_highscore")
        self.high_score = self.load_high_score()
        
        # Physics and Constants
        self.gravity = 0.42
        self.jump_strength = -7.5
        self.max_fall_speed = 10.0
        self.ground_height = 80
        self.pipe_speed = 3.2
        self.pipe_gap = 150
        self.pipe_width = 75
        self.pipe_spawn_interval = 110  # frames (approx 1.8 seconds)
        
        # Game Variables
        self.state = "START_SCREEN"  # START_SCREEN, PLAYING, GAME_OVER
        self.frame_count = 0
        self.score = 0
        
        # Player (Bird) variables
        self.bird_x = 120
        self.bird_y = 250
        self.bird_velocity = 0
        self.bird_angle = 0.0
        self.bird_radius = 16
        
        # Parallax Background Lists
        self.clouds = []
        self.buildings = []
        self.pipes = []
        self.ground_details = []
        self.popups = []  # floating score popups
        
        # Screen effects
        self.shake_remaining = 0
        self.flash_opacity = 0.0
        
        # Initialize background layers
        self.init_background_layers()
        
        # Start game loop
        self.update()

    def load_high_score(self):
        try:
            if os.path.exists(self.highscore_file):
                with open(self.highscore_file, "r") as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            with open(self.highscore_file, "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def init_background_layers(self):
        # 1. Clouds (Parallax Layer 1 - slowest)
        self.clouds = [
            {"x": 60, "y": 80, "scale": 1.2, "speed": 0.4},
            {"x": 220, "y": 140, "scale": 0.8, "speed": 0.3},
            {"x": 380, "y": 60, "scale": 1.0, "speed": 0.5},
            {"x": 520, "y": 110, "scale": 1.1, "speed": 0.35}
        ]
        
        # 2. Skyline Buildings (Parallax Layer 2 - moderate)
        # We spawn a continuous horizon of buildings
        colors = ["#4ea7b2", "#3a96a1", "#2d8792"]
        x = 0
        while x < self.width + 200:
            width = random.randint(50, 90)
            height = random.randint(120, 220)
            self.buildings.append({
                "x": x,
                "width": width,
                "height": height,
                "color": random.choice(colors),
                "speed": 0.9
            })
            x += width
            
        # 3. Ground Grass details (moves at full speed)
        for i in range(12):
            self.ground_details.append({
                "x": i * 45,
                "width": 12,
                "height": random.randint(8, 16)
            })

    def start_game(self):
        self.state = "PLAYING"
        self.score = 0
        self.bird_y = 250
        self.bird_velocity = 0
        self.bird_angle = 0.0
        self.pipes = []
        self.popups = []
        self.shake_remaining = 0
        self.flash_opacity = 0.0
        self.frame_count = 0

    def restart_event(self, event):
        if self.state == "GAME_OVER":
            self.start_game()

    def jump(self, event):
        if self.state == "START_SCREEN":
            self.start_game()
        elif self.state == "PLAYING":
            self.bird_velocity = self.jump_strength
            # Small rotation boost upwards immediately
            self.bird_angle = -0.3
        elif self.state == "GAME_OVER":
            # Allow jumping to restart as well for classic arcade feel
            self.start_game()

    def trigger_crash(self):
        self.state = "GAME_OVER"
        self.shake_remaining = 10  # Activate screen shake
        self.flash_opacity = 0.9   # Activate bright white flash
        
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def rotate_point(self, px, py, cx, cy, angle_rad):
        # Rotate point (px, py) around center (cx, cy)
        s = math.sin(angle_rad)
        c = math.cos(angle_rad)
        # Translate to origin
        dx = px - cx
        dy = py - cy
        # Rotate
        rx = dx * c - dy * s
        ry = dx * s + dy * c
        # Translate back
        return cx + rx, cy + ry

    def update(self):
        self.frame_count += 1
        
        # --- Game State Physics & Calculations ---
        if self.state == "PLAYING":
            # Apply Gravity
            self.bird_velocity += self.gravity
            if self.bird_velocity > self.max_fall_speed:
                self.bird_velocity = self.max_fall_speed
            self.bird_y += self.bird_velocity
            
            # Smoothly interpolate bird tilt based on speed
            # Tilts up when flying (-), nose dives when falling (+)
            target_angle = max(-0.4, min(1.2, self.bird_velocity * 0.08))
            self.bird_angle += (target_angle - self.bird_angle) * 0.18
            
            # Move Parallax Background layers
            # Clouds
            for cloud in self.clouds:
                cloud["x"] -= cloud["speed"]
                if cloud["x"] < -120:
                    cloud["x"] = self.width + 80
                    cloud["y"] = random.randint(40, 160)
            
            # Buildings
            for bldg in self.buildings:
                bldg["x"] -= bldg["speed"]
            # Recycle buildings that left the screen
            self.buildings.sort(key=lambda b: b["x"])
            if self.buildings[0]["x"] + self.buildings[0]["width"] < 0:
                leftmost = self.buildings.pop(0)
                rightmost = self.buildings[-1]
                leftmost["x"] = rightmost["x"] + rightmost["width"]
                leftmost["height"] = random.randint(120, 220)
                self.buildings.append(leftmost)
                
            # Ground grass details
            for detail in self.ground_details:
                detail["x"] -= self.pipe_speed
                if detail["x"] < -20:
                    detail["x"] = self.width + random.randint(10, 30)
                    detail["height"] = random.randint(8, 16)
                    
            # Pipe spawning
            if self.frame_count % self.pipe_spawn_interval == 0:
                # Calculate heights
                top_limit = 50
                bottom_limit = self.height - self.ground_height - self.pipe_gap - 50
                top_height = random.randint(top_limit, bottom_limit)
                bottom_y = top_height + self.pipe_gap
                self.pipes.append({
                    "x": self.width + 20,
                    "top_height": top_height,
                    "bottom_y": bottom_y,
                    "passed": False
                })
                
            # Move Pipes
            for pipe in self.pipes:
                pipe["x"] -= self.pipe_speed
                
            # Filter off-screen pipes
            self.pipes = [p for p in self.pipes if p["x"] > -self.pipe_width - 10]
            
            # Check collisions
            self.check_collisions()
            
            # Score check and Float Popups update
            bird_left = self.bird_x - self.bird_radius
            for pipe in self.pipes:
                if not pipe["passed"] and pipe["x"] + self.pipe_width // 2 < self.bird_x:
                    pipe["passed"] = True
                    self.score += 1
                    # Spawn visual score popup (+1)
                    self.popups.append({
                        "x": pipe["x"] + self.pipe_width // 2,
                        "y": self.bird_y - 25,
                        "text": "+1",
                        "timer": 35
                    })
                    
            # Update floating score popups
            for popup in self.popups:
                popup["y"] -= 0.8
                popup["timer"] -= 1
            self.popups = [p for p in self.popups if p["timer"] > 0]
            
        elif self.state == "START_SCREEN":
            # Gentle floating effect for bird on start screen
            self.bird_y = 250 + math.sin(self.frame_count * 0.08) * 12
            self.bird_angle = math.sin(self.frame_count * 0.08) * 0.1
            
            # Move clouds slowly on start screen for a living world
            for cloud in self.clouds:
                cloud["x"] -= cloud["speed"]
                if cloud["x"] < -120:
                    cloud["x"] = self.width + 80
                    cloud["y"] = random.randint(40, 160)

        # Screen shake dampening
        if self.shake_remaining > 0:
            self.shake_remaining -= 1
            
        # Screen flash fading
        if self.flash_opacity > 0.0:
            self.flash_opacity -= 0.1
            if self.flash_opacity < 0.0:
                self.flash_opacity = 0.0

        # --- DRAWING / RENDERING ---
        self.canvas.delete("all")
        
        # Calculate screen shake offsets
        dx, dy = 0, 0
        if self.shake_remaining > 0:
            dx = random.choice([-5, 0, 5])
            dy = random.choice([-5, 0, 5])

        # 1. Clouds
        for cloud in self.clouds:
            cx, cy = cloud["x"] + dx, cloud["y"] + dy
            scale = cloud["scale"]
            # Draw a fluffy cloud using 4 overlapping circles
            self.canvas.create_oval(cx - 30*scale, cy - 10*scale, cx + 30*scale, cy + 35*scale, fill="#ffffff", outline="")
            self.canvas.create_oval(cx - 45*scale, cy + 5*scale, cx + 5*scale, cy + 35*scale, fill="#ffffff", outline="")
            self.canvas.create_oval(cx, cy + 5*scale, cx + 45*scale, cy + 35*scale, fill="#ffffff", outline="")
            self.canvas.create_oval(cx - 20*scale, cy - 20*scale, cx + 20*scale, cy + 20*scale, fill="#ffffff", outline="")

        # 2. Skyline Buildings (Parallax Background)
        for bldg in self.buildings:
            bx = bldg["x"] + dx
            by = self.height - self.ground_height - bldg["height"] + dy
            self.canvas.create_rectangle(
                bx, by, 
                bx + bldg["width"], self.height - self.ground_height + dy, 
                fill=bldg["color"], outline=""
            )
            # Subtle window details on buildings to make them look premium
            win_cols = bldg["width"] // 14
            win_rows = bldg["height"] // 25
            for r in range(min(win_rows, 5)):
                for c in range(min(win_cols, 4)):
                    wx = bx + 6 + c * 14
                    wy = by + 8 + r * 22
                    self.canvas.create_rectangle(wx, wy, wx + 6, wy + 10, fill="#78ccd6", outline="")

        # 3. Pipes
        for pipe in self.pipes:
            px = pipe["x"] + dx
            # Top Pipe
            top_y = pipe["top_height"] + dy
            # Main pipe shaft
            self.canvas.create_rectangle(px + 4, dy, px + self.pipe_width - 4, top_y - 20, fill="#73bf2e", outline="#27ae60", width=2)
            # 3D Highlight Shine
            self.canvas.create_rectangle(px + 12, dy, px + 22, top_y - 20, fill="#a2e75c", outline="")
            # Pipe End Cap (Lip)
            self.canvas.create_rectangle(px, top_y - 20, px + self.pipe_width, top_y, fill="#73bf2e", outline="#27ae60", width=2)
            self.canvas.create_rectangle(px + 8, top_y - 18, px + 18, top_y - 2, fill="#a2e75c", outline="")
            
            # Bottom Pipe
            bot_y = pipe["bottom_y"] + dy
            # Main pipe shaft
            self.canvas.create_rectangle(px + 4, bot_y + 20, px + self.pipe_width - 4, self.height - self.ground_height + dy, fill="#73bf2e", outline="#27ae60", width=2)
            # 3D Highlight Shine
            self.canvas.create_rectangle(px + 12, bot_y + 20, px + 22, self.height - self.ground_height + dy, fill="#a2e75c", outline="")
            # Pipe End Cap (Lip)
            self.canvas.create_rectangle(px, bot_y, px + self.pipe_width, bot_y + 20, fill="#73bf2e", outline="#27ae60", width=2)
            self.canvas.create_rectangle(px + 8, bot_y + 2, px + 18, bot_y + 18, fill="#a2e75c", outline="")

        # 4. Ground Platform
        gy = self.height - self.ground_height + dy
        # Dirt layer
        self.canvas.create_rectangle(0, gy, self.width, self.height, fill="#ded895", outline="#cbbd70", width=2)
        # Underground dark line detailing
        for i in range(10):
            ox = (i * 60 + (self.frame_count * 1.5 if self.state == "PLAYING" else 0)) % (self.width + 100) - 50
            self.canvas.create_line(ox, gy + 30, ox - 20, gy + 70, fill="#c0b560", width=3)
            
        # Grass layer (Top of Ground)
        self.canvas.create_rectangle(0, gy, self.width, gy + 15, fill="#73bf2e", outline="#5c9e22", width=1)
        # Moving Grass Details (Blades of grass scrolling left)
        for detail in self.ground_details:
            dx_grass = detail["x"] + dx
            self.canvas.create_rectangle(dx_grass, gy, dx_grass + detail["width"], gy + 6, fill="#5c9e22", outline="")

        # 5. Animated & Rotated Bird
        bx = self.bird_x + dx
        by = self.bird_y + dy
        
        # Rotate and gather coordinates of bird elements
        # 5a. Orange Beak
        b1_x, b1_y = self.rotate_point(bx + 11, by - 5, bx, by, self.bird_angle)
        b2_x, b2_y = self.rotate_point(bx + 23, by, bx, by, self.bird_angle)
        b3_x, b3_y = self.rotate_point(bx + 11, by + 5, bx, by, self.bird_angle)
        self.canvas.create_polygon(b1_x, b1_y, b2_x, b2_y, b3_x, b3_y, fill="#f75300", outline="#b33c00", width=2)
        
        # 5b. Yellow Round Body
        self.canvas.create_oval(bx - self.bird_radius, by - self.bird_radius, bx + self.bird_radius, by + self.bird_radius, fill="#fcdb1e", outline="#d5a100", width=2.5)
        # Belly highlight (slightly lighter yellow dome)
        self.canvas.create_arc(bx - self.bird_radius + 2, by - self.bird_radius + 2, bx + self.bird_radius - 2, by + self.bird_radius - 2, start=180, extent=180, fill="#fff275", outline="")

        # 5c. Big Eye & Pupil
        ex, ey = self.rotate_point(bx + 6, by - 6, bx, by, self.bird_angle)
        self.canvas.create_oval(ex - 6, ey - 6, ex + 6, ey + 6, fill="#ffffff", outline="#000000", width=1.5)
        
        px, py = self.rotate_point(bx + 8, by - 6, bx, by, self.bird_angle)
        self.canvas.create_oval(px - 2.5, py - 2.5, px + 2.5, py + 2.5, fill="#000000", outline="")

        # 5d. Wing with animated flap oscillation
        flap_offset = 0
        if self.state == "PLAYING" or self.state == "START_SCREEN":
            # Oscillate height of the wing using sine wave to represent rapid flapping
            flap_offset = math.sin(self.frame_count * 0.45) * 5.5
            
        w1_x, w1_y = self.rotate_point(bx - 14, by, bx, by, self.bird_angle)
        w2_x, w2_y = self.rotate_point(bx - 6, by - 8 - flap_offset, bx, by, self.bird_angle)
        w3_x, w3_y = self.rotate_point(bx - 2, by, bx, by, self.bird_angle)
        w4_x, w4_y = self.rotate_point(bx - 6, by + 8 + flap_offset, bx, by, self.bird_angle)
        
        self.canvas.create_polygon(w1_x, w1_y, w2_x, w2_y, w3_x, w3_y, w4_x, w4_y, fill="#ffffff", outline="#d5a100", width=2, smooth=True)

        # 6. Floating Score Popups
        for popup in self.popups:
            px_pop = popup["x"] + dx
            py_pop = popup["y"] + dy
            # Shadow
            self.canvas.create_text(px_pop + 1.5, py_pop + 1.5, text=popup["text"], font=("Helvetica", 14, "bold"), fill="#222222")
            # Highlight Text
            self.canvas.create_text(px_pop, py_pop, text=popup["text"], font=("Helvetica", 14, "bold"), fill="#fcdb1e")

        # 7. UI Overlays and Text
        if self.state == "START_SCREEN":
            # Bouncing Logo Title
            logo_y = 120 + math.sin(self.frame_count * 0.05) * 6
            # Logo Shadow
            self.canvas.create_text(self.width // 2 + 3, logo_y + 3, text="FLAPPY BIRD", font=("Helvetica", 36, "bold"), fill="#27707c")
            # Logo Main
            self.canvas.create_text(self.width // 2, logo_y, text="FLAPPY BIRD", font=("Helvetica", 36, "bold"), fill="#ffffff")
            
            # Blinking instructions
            blink = (self.frame_count // 25) % 2 == 0
            inst_text = "PRESS SPACE TO FLAP" if blink else ""
            self.canvas.create_text(self.width // 2 + 1, 361, text=inst_text, font=("Helvetica", 16, "bold"), fill="#27707c")
            self.canvas.create_text(self.width // 2, 360, text=inst_text, font=("Helvetica", 16, "bold"), fill="#ffffff")
            
            # High Score Display
            self.canvas.create_text(self.width // 2 + 1, 461, text=f"HIGH SCORE: {self.high_score}", font=("Helvetica", 13, "bold"), fill="#27707c")
            self.canvas.create_text(self.width // 2, 460, text=f"HIGH SCORE: {self.high_score}", font=("Helvetica", 13, "bold"), fill="#fcdb1e")

        elif self.state == "PLAYING":
            # Large clean score counter HUD
            # Shadow
            self.canvas.create_text(self.width // 2 + 2, 52, text=str(self.score), font=("Helvetica", 42, "bold"), fill="#222222")
            # Text
            self.canvas.create_text(self.width // 2, 50, text=str(self.score), font=("Helvetica", 42, "bold"), fill="#ffffff")

        elif self.state == "GAME_OVER":
            # Dark modern glassmorphism overlay card
            self.canvas.create_rectangle(60, 140, self.width - 60, 480, fill="#2c3e50", outline="#1abc9c", width=3, stipple="")
            
            # GAME OVER Title
            self.canvas.create_text(self.width // 2, 190, text="GAME OVER", font=("Helvetica", 28, "bold"), fill="#e74c3c")
            
            # Score details Card
            card_bg = "#34495e"
            self.canvas.create_rectangle(90, 240, self.width - 90, 390, fill=card_bg, outline="", width=0)
            
            # Score texts inside card
            self.canvas.create_text(self.width // 2, 275, text="FINAL SCORE", font=("Helvetica", 11, "bold"), fill="#bdc3c7")
            self.canvas.create_text(self.width // 2, 305, text=str(self.score), font=("Helvetica", 26, "bold"), fill="#ffffff")
            
            # Check if new high score
            is_new_high = (self.score == self.high_score and self.score > 0)
            hs_color = "#f1c40f" if is_new_high else "#ffffff"
            hs_label = "🏆 NEW HIGH SCORE 🏆" if is_new_high else "BEST SCORE"
            
            self.canvas.create_text(self.width // 2, 345, text=hs_label, font=("Helvetica", 10, "bold"), fill="#f1c40f" if is_new_high else "#bdc3c7")
            self.canvas.create_text(self.width // 2, 370, text=str(self.high_score), font=("Helvetica", 16, "bold"), fill=hs_color)
            
            # Pulsing restart text
            blink_restart = (self.frame_count // 20) % 2 == 0
            restart_msg = "PRESS 'R' TO RESTART" if blink_restart else "PRESS 'R' TO RESTART" # keep solid but readable
            self.canvas.create_text(self.width // 2, 440, text=restart_msg, font=("Helvetica", 13, "bold"), fill="#1abc9c")

        # 8. Render Screen Crash Flash
        if self.flash_opacity > 0.0:
            # We draw a white canvas-wide block to represent the impact flash
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#ffffff", outline="")

        # Refresh Game Loop at 60 FPS (approx 16ms)
        self.root.after(16, self.update)

    def check_collisions(self):
        # 1. Collision with Ground
        if self.bird_y + self.bird_radius >= self.height - self.ground_height:
            self.bird_y = self.height - self.ground_height - self.bird_radius
            self.trigger_crash()
            return
            
        # 2. Collision with Top Ceiling
        if self.bird_y - self.bird_radius <= 0:
            self.bird_y = self.bird_radius
            self.trigger_crash()
            return
            
        # 3. Collision with Pipes (Forgiving Hitboxes)
        # Bounding box of bird with small margin
        margin = 3
        bx1 = self.bird_x - self.bird_radius + margin
        bx2 = self.bird_x + self.bird_radius - margin
        by1 = self.bird_y - self.bird_radius + margin
        by2 = self.bird_y + self.bird_radius - margin
        
        for pipe in self.pipes:
            px1 = pipe["x"]
            px2 = pipe["x"] + self.pipe_width
            
            # Check horizontal overlap with pipe
            if bx2 > px1 and bx1 < px2:
                # Collision with upper pipe
                if by1 < pipe["top_height"]:
                    self.trigger_crash()
                    return
                # Collision with lower pipe
                if by2 > pipe["bottom_y"]:
                    self.trigger_crash()
                    return

if __name__ == "__main__":
    root = tk.Tk()
    app = FlappyBirdGame(root)
    root.mainloop()
