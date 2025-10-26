import pygame, sys, math, random

pygame.init()
WIDTH, HEIGHT = 960, 540
Window =  pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Práctica 5 - Fondos y Animaciones")
Clock = pygame.time.Clock()
FPS = 60

# ------------------- UTILIDADES -------------------
def make_text(txt, size=20, color=(230,230,240)):
    return pygame.font.SysFont(None, size).render(txt, True, color)

def clamp(v, a, b):
    return max(a, min(v, b))

def lerp_color(c1, c2, t):
    """Interpola linealmente entre dos colores."""
    r = int(c1[0] * (1 - t) + c2[0] * t)
    g = int(c1[1] * (1 - t) + c2[1] * t)
    b = int(c1[2] * (1 - t) + c2[2] * t)
    return (r, g, b)

# ------------------- CAPAS DE FONDO  -------------------
class BaseLayer:
    """Clase base para una capa de fondo con scroll parallax."""
    def __init__(self, w, h, speed):
        self.w, self.h = w, h
        self.speed = speed
        self.offset = 0.0
        self.surf = pygame.Surface((w * 2, h), pygame.SRCALPHA)

    def update(self, camera_x):
        self.offset = (camera_x * self.speed) % self.w

    def draw(self, screen):
        draw_x = int(self.offset)
        screen.blit(self.surf, (-draw_x, 0))
        screen.blit(self.surf, (-draw_x + self.w, 0))

class StarLayer(BaseLayer):
    """Capa de estrellas en movimiento"""
    def __init__(self, w, h, density=0.0008, speed=0.4):
        super().__init__(w, h, speed)
        count = int(w*h*density)
        for _ in range(count):
            x = random.randint(0, w*2-1)
            y = random.randint(0, h-1)
            c = random.randint(180, 255)
            self.surf.set_at((x,y), (c,c,c,255))
    
class HillsLayer(BaseLayer):
    """Capa de colinas dibujadas con polígono, parallax."""
    def __init__(self, w, h, color=(40,80,60), base=420, amp=28, freq=0.012, speed=1.0):
        super().__init__(w, h, speed)
        self.color = color
        self.base = base
        self.amp = amp
        self.freq = freq
        self._render()        
        
    def _render(self):
        self.surf.fill((0,0,0,0))
        for x in range(self.w*2):
            y = int(self.base + math.sin((x)*self.freq) * self.amp)
            pygame.draw.line(self.surf, self.color, (x, y), (x, self.h))

        # Suaviza el borde superior (hecho una vez fuera del bucle para eficiencia)
        overlay = pygame.Surface((self.w*2, self.h), pygame.SRCALPHA)
        overlay.fill((*self.color, 30))
        self.surf.blit(overlay, (0,0))

class CloudsLayer(BaseLayer):
    """Capa de 'nubes' translúcidas que se repiten."""
    def __init__(self, w, h, speed=1.8, count=10):
        super().__init__(w, h, speed)
        for _ in range(count):
            cx = random.randint(0, w*2-1)
            cy = random.randint(40, h//2)
            r = random.randint(20, 60)
            cloud = pygame.Surface((r*4, r*2), pygame.SRCALPHA)
            for i in range(6):
                pygame.draw.circle(cloud, (255,255,255,60), (random.randint(r, r*3), random.randint(r//2, r)), random.randint(r//2, r))
            self.surf.blit(cloud, (cx, cy))


# ------------------- PARTÍCULAS -------------------
class Particle:
    """Representa una sola partícula de polvo."""
    def __init__(self, pos, vel, radius, color, lifetime):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius = radius
        self.color = color
        self.lifetime = lifetime
        self.initial_lifetime = lifetime

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt
        # La partícula se encoge y se desvanece con el tiempo
        self.radius = max(0, self.radius * (self.lifetime / self.initial_lifetime))

    def draw(self, screen, camera_x):
        if self.radius > 0:
            screen_pos = (self.pos.x - camera_x, self.pos.y)
            pygame.draw.circle(screen, self.color, screen_pos, int(self.radius))

class ParticleEmitter:
    """Gestiona la creación, actualización y dibujado de partículas."""
    def __init__(self):
        self.particles = []

    def emit(self, pos, direction):
        color = (140, 120, 90, 100) # Color de polvo
        for _ in range(random.randint(3, 6)):
            vel = pygame.Vector2(direction * random.uniform(20, 50), random.uniform(-40, -10))
            self.particles.append(Particle(pos, vel, random.uniform(3, 7), color, random.uniform(0.4, 0.8)))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for p in self.particles:
            p.update(dt)

    def draw(self, screen, camera_x):
        for p in self.particles:
            p.draw(screen, camera_x)
        
# ------------------- SPRITE ANIMADO -------------------
def make_idle_frames(size=(48,48)):
    """Genera frames 'idle' simples (boteo) sin assets externos."""
    w,h = size
    frames = []
    for i in range(6):
        surf = pygame.Surface((w,h), pygame.SRCALPHA)
        #cuerpo
        pygame.draw.rect(surf, (240, 220, 90), (8, 12, w-16, h-20), border_radius=10)
        # cara/bote
        dy = int(math.sin(i/6*math.tau)*2)
        pygame.draw.circle(surf, (30,30,30), (w//2-6, 18+dy), 4)
        pygame.draw.circle(surf, (30,30,30), (w//2+6, 18+dy), 4)
        pygame.draw.rect(surf, (30,30,30), (w//2-8, 22+dy, 16, 3), border_radius=2)
        frames.append(surf)
    return frames

def make_run_frames(size=(48,48)):
    """Genera frames 'run' básicos (brazos/piernas)."""
    w,h = size
    frames = []
    for i in range(8):
        surf = pygame.Surface((w,h), pygame.SRCALPHA)
        # cuerpo
        pygame.draw.rect(surf, (240, 120, 90), (8, 8, w-16, h-16), border_radius=10)
        phase = i/8*math.tau
        arm = int(math.sin(phase)*6)
        leg = int(math.cos(phase)*6)
        # brazos
        pygame.draw.rect(surf, (60,60,60), (4, 18+arm, 10, 6), border_radius=3)
        pygame.draw.rect(surf, (60,60,60), (w-14, 18-arm, 10, 6), border_radius=3)
        # piernas
        pygame.draw.rect(surf, (40,40,40), (12, h-14+leg, 10, 6), border_radius=2)
        pygame.draw.rect(surf, (40,40,40), (w-22, h-14-leg, 10, 6), border_radius=2)
        #ojos
        pygame.draw.circle(surf, (30,30,30), (w//2-6, 18), 4)
        pygame.draw.circle(surf, (30,30,30), (w//2+6, 18), 4)
        frames.append(surf)
    return frames

def make_jump_frames(size=(48,48)):
    """Genera un frame de 'salto'."""
    w,h = size
    surf = pygame.Surface((w,h), pygame.SRCALPHA)
    # Cuerpo aplastado/estirado para dar sensación de salto
    pygame.draw.rect(surf, (240, 180, 90), (8, 16, w-16, h-20), border_radius=10)
    # Ojos abiertos
    pygame.draw.circle(surf, (255,255,255), (w//2-7, 18), 5)
    pygame.draw.circle(surf, (255,255,255), (w//2+7, 18), 5)
    pygame.draw.circle(surf, (30,30,30), (w//2-7, 18), 2)
    pygame.draw.circle(surf, (30,30,30), (w//2+7, 18), 2)
    return [surf] # Devolvemos una lista con un solo frame

def load_sprite_sheet(filename, frame_width, frame_height, frame_count):
    """Carga y corta una hoja de sprites horizontal."""
    frames = []
    try:
        # Carga la hoja de sprites completa
        sheet = pygame.image.load(filename).convert_alpha()
        
        # Itera a través de la hoja y corta cada frame
        for i in range(frame_count):
            x_pos = i * frame_width
            # Corta el frame usando subsurface
            frame = sheet.subsurface((x_pos, 0, frame_width, frame_height))
            frames.append(frame)
            
    except Exception as e:
        print(f"Error al cargar la hoja de sprites {filename}: {e}")
        # Genera frames de respaldo simples si falla la carga
        frames = make_idle_frames((frame_width, frame_height)) # Fallback
        
    return frames

class AnimSprite(pygame.sprite.Sprite):
    def __init__(self, pos, particle_emitter):
        super().__init__()
        self.particle_emitter = particle_emitter
        self.frames_idle = load_sprite_sheet("Biker_idle.png", 48, 48, 4) or make_idle_frames()
        self.frames_run  = load_sprite_sheet("Biker_run.png",  48, 48, 6) or make_run_frames()
        self.frames_jump = load_sprite_sheet("Biker_jump.png", 48, 48, 4) or make_jump_frames()
        self.frames = self.frames_idle
        self.frame_index = 0
        self.frame_time = 0.0
        self.frame_duration = 0.1 # s por frame
        self.image = self.frames [0]
        self.rect = self.image.get_rect(center=pos)
        # movimiento
        self.vel = pygame.Vector2(0,0)
        self.accel = 0.7
        self.friction = 0.86
        self.max_speed = 6.5
        self.facing_left = False
        # Física de salto
        self.ground_y = pos[1]
        self.gravity = 0.7
        self.jump_strength = -15
        self.is_on_ground = True
        # Timer para partículas de polvo
        self.dust_emission_rate = 0.12 # segundos entre emisiones
        self.dust_timer = 0.0
 
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x -= self.accel
            self.facing_left = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x += self.accel
            self.facing_left = False
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.is_on_ground:
            self.vel.y = self.jump_strength
            self.is_on_ground = False
    
    def apply_physics(self):
        # Física horizontal
        self.vel.x = clamp(self.vel.x, -self.max_speed, self.max_speed)
        self.vel *= self.friction
        self.rect.x += int(self.vel.x)
        
        # Física vertical (gravedad y suelo)
        if not self.is_on_ground:
            self.vel.y += self.gravity
            self.rect.y += self.vel.y
        
        # Colisión con el suelo
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vel.y = 0
            self.is_on_ground = True
            
        
    def choose_animation(self):
        if not self.is_on_ground:
            target = self.frames_jump
        else:
            target = self.frames_run if abs(self.vel.x) > 0.2 else self.frames_idle
            
        if target is not self.frames:
            self.frames = target
            # Para el salto, no queremos que el índice se reinicie si ya estamos en el aire
            if target is not self.frames_jump:
                self.frame_index = 0
            self.frame_time = 0.0
            # animación 'run' es más rápida que 'idle'
            if target is self.frames_idle:
                self.frame_duration = 0.12
            elif target is self.frames_run:
                self.frame_duration = 0.08
            elif target is self.frames_jump:
                self.frame_duration = 0.1 # Duración por frame de salto

    def handle_particles(self, dt):
        self.dust_timer += dt
        is_running_on_ground = self.is_on_ground and abs(self.vel.x) > 1.5
        if is_running_on_ground and self.dust_timer > self.dust_emission_rate:
            self.dust_timer = 0.0
            particle_pos = (self.rect.centerx, self.rect.bottom - 5)
            particle_direction = 1 if self.facing_left else -1
            self.particle_emitter.emit(particle_pos, particle_direction)
            
    def animate(self, dt):
        self.frame_time += dt
        if self.frame_time > self.frame_duration:
            self.frame_time -= self.frame_duration
            # La animación de salto no se repite, las otras sí
            if self.frames is self.frames_jump:
                # Avanza el frame de salto pero no pasa del último
                self.frame_index = min(self.frame_index + 1, len(self.frames) - 1)
            else:
                # Animaciones en bucle
                self.frame_index = (self.frame_index + 1) % len(self.frames)
            
        # Asigna la imagen actual y la voltea si es necesario
        current_frame = self.frames[self.frame_index]
        self.image = pygame.transform.flip(current_frame, self.facing_left, False)

    def update(self, dt):
        self.handle_input()
        self.apply_physics()
        self.choose_animation()
        self.handle_particles(dt)
        self.animate(dt)

    def draw(self, screen, camera_x):
        screen_x = self.rect.x - camera_x # Calcula la posición en pantalla relativa a la cámara
        screen.blit(self.image, (screen_x, self.rect.y))

class TreesLayer(BaseLayer):
    """Capa de 'árboles' en primer plano (se mueven rápido)."""
    def __init__(self, w, h, speed=3.5, count=15):
        super().__init__(w, h, speed)
        
        ground_line = 480 # Dónde "plantar" los árboles
        
        for _ in range(count):
            x = random.randint(0, w * 2 - 1)
            tree_height = random.randint(60, 150)
            trunk_width = random.randint(6, 12)
            
            # Dibujar tronco
            trunk_color = (60, 40, 30) # Marrón oscuro
            pygame.draw.rect(self.surf, trunk_color, (x, ground_line - tree_height, trunk_width, tree_height))
            
            # Dibujar hojas (círculo)
            leaf_color = (20, 100, 40, 200) # Verde oscuro translúcido
            leaf_radius = random.randint(20, 40)
            pygame.draw.circle(self.surf, leaf_color, (x + trunk_width // 2, ground_line - tree_height), leaf_radius)

class DayNightManager:
    """Gestiona el ciclo día/noche y los colores del cielo."""
    def __init__(self, cycle_duration_seconds=60):
        self.cycle_duration = cycle_duration_seconds
        self.time_of_day = 0.0  # 0.0 (medianoche) a 1.0 (siguiente medianoche)

        # (top_color, bottom_color)
        self.colors = {
            "night": ((10, 12, 22), (25, 28, 48)),
            "dawn":  ((50, 60, 100), (130, 80, 100)),
            "day":   ((135, 206, 235), (200, 220, 240)),
            "dusk":  ((255, 120, 50), (100, 80, 120)),
        }
        self.keyframes = [
            (0.0, "night"), (0.25, "dawn"), (0.5, "day"), (0.75, "dusk"), (1.0, "night")
        ]
        self.current_top = self.colors["night"][0]
        self.current_bottom = self.colors["night"][1]

    def update(self, dt):
        self.time_of_day = (self.time_of_day + dt / self.cycle_duration) % 1.0

        # Encontrar los dos keyframes actuales
        for i in range(len(self.keyframes) - 1):
            start_time, start_name = self.keyframes[i]
            end_time, end_name = self.keyframes[i+1]

            if start_time <= self.time_of_day < end_time:
                # Calcular el progreso (t) entre los dos keyframes
                time_range = end_time - start_time
                progress_in_range = self.time_of_day - start_time
                t = progress_in_range / time_range

                # Interpolar los colores
                self.current_top = lerp_color(self.colors[start_name][0], self.colors[end_name][0], t)
                self.current_bottom = lerp_color(self.colors[start_name][1], self.colors[end_name][1], t)
                break


# --------------------- ESCENA -----------------------
def draw_gradient_bg(screen, top=(10,12,22), bottom=(25,28,48)):
    """Fondo con degradado vertical rápido."""
    for y in range(HEIGHT):
        t = y/HEIGHT
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
        
        
def main():
    # Capas de fondo
    stars_far = StarLayer(WIDTH, HEIGHT, density=0.0010, speed=0.25)
    clouds = CloudsLayer(WIDTH, HEIGHT, speed=1.2, count=10)
    hills = HillsLayer(WIDTH, HEIGHT, color=(35, 90, 70), base=400, amp=36, freq=0.010, speed=2.0)
    foreground_trees = TreesLayer(WIDTH, HEIGHT, speed=3.5)
    
    particle_emitter = ParticleEmitter()
    player = AnimSprite((WIDTH//2, 460), particle_emitter) # Ajustamos la posición inicial al suelo
    group = pygame.sprite.Group(player)
    
    day_night_manager = DayNightManager(cycle_duration_seconds=120) # Ciclo de 2 minutos

    camera_x = 0 # Posición horizontal de la cámara en el mundo
    
    running = True
    while running:
        dt_ms = Clock.tick(FPS)
        dt = dt_ms/1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Actualizar el jugador (su rect.x es ahora su posición en el mundo)
        group.update(dt)

        # Calcular la posición de la cámara para centrar al jugador
        # camera_x representa la coordenada mundial del borde izquierdo de la pantalla
        camera_x = player.rect.centerx - (WIDTH // 2)

        # Actualizar las capas de fondo con la posición de la cámara
        stars_far.update(camera_x)
        clouds.update(camera_x)
        hills.update(camera_x)
        foreground_trees.update(camera_x)
        day_night_manager.update(dt)
        particle_emitter.update(dt)
        
        #Draw
        draw_gradient_bg(Window, day_night_manager.current_top, day_night_manager.current_bottom)
        stars_far.draw(Window)
        clouds.draw(Window)
        hills.draw(Window)
        particle_emitter.draw(Window, camera_x)
        player.draw(Window, camera_x) # Dibujar el jugador usando la cámara
        foreground_trees.draw(Window)
        
        #HUD
        time_str = f"{int(day_night_manager.time_of_day * 24):02d}:{int((day_night_manager.time_of_day * 24 * 60) % 60):02d}"
        hud = [
            "Práctica 4 - Fondos y Animaciones",
            f"FPS: {int(Clock.get_fps())} | Time: {time_str}",
            "Izq/Der o A/D para mover | Espacio/Arriba para saltar",
            "Esc para salir | Consejo: observa el parallax."
            
        ]
        for i, line in enumerate(hud):
            Window.blit(make_text(line, 20), (10, 10 + i*22))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()
    
# ------------------- Retos/Extenciones -------------------
# 1) Sprite sheet real: carga una hoja (PNG) y corta frames con subsurface. ya
# 2) Estado 'salto' (JUMP): agrega una animación y física vertical simple (gravedad). si
# 3) Parallax 4+ capas: agrega una capa de ciudad/montañas extra al frente.   ya
# 4) Cámara: desplaza el mundo según la posición del jugador y repite fondo infinito. si
# 5) Control de tiempo: usa acumulador para animación independiente del FPS. si
# 6) Transiciones día/noche: modifica el gradiente y alfa de nubes con un ciclo. si
# 7) Efectos: agrega partículas al correr (polvo) que desaparezcan con el tiempo. si