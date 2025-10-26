Práctica 4 - README: Fondos y Animaciones
Este documento detalla las justificaciones de los parámetros clave y las extensiones implementadas en el proyecto, como lo solicita la rúbrica.
Velocidades por Capa (Parallax) y Justificación
Para crear una ilusión de profundidad convincente (efecto parallax), se configuraron 4 capas de fondo que se mueven a diferentes velocidades relativas a la cámara. La regla es: a mayor velocidad, más cerca parece estar la capa.
StarLayer (stars_far): speed = 0.25
Justificación: Es la capa más lenta y, por lo tanto, la más lejana. Simula estrellas o un fondo de cielo muy distante que apenas se mueve.
CloudsLayer (clouds): speed = 1.2
Justificación: Una capa de nubes lejanas que se mueven ligeramente más rápido que las estrellas, creando una primera capa de profundidad.
HillsLayer (hills): speed = 2.0
Justificación: Esta es la capa de fondo principal (las colinas). Su velocidad es notable y establece el plano general de la escena.
TreesLayer (foreground_trees): speed = 3.5
Justificación: Esta es la capa más rápida. Al moverse más rápido que el jugador y el resto del fondo, actúa como un primer plano (foreground). Los árboles pasan "por delante" del jugador, dando la sensación de profundidad más fuerte y un efecto 3D muy claro.
La separación entre estos valores (0.25, 1.2, 2.0, 3.5) asegura que cada capa sea visualmente distinta, maximizando el efecto parallax.

frame_duration por Estado (Idle/Run/Jump) y Justificación
El frame_duration (medido en segundos) se ajustó de forma diferente para cada estado del jugador para darle el "peso" y la "sensación" adecuados a cada acción.
Estado idle (Quieto): frame_duration = 0.12 (120 ms)
Justificación: Se eligió un tiempo más largo para que la animación de "quieto" (ya sea respirando o, en este caso, la animación del sprite sheet "Biker_idle") se sienta relajada y natural. Un valor más corto la haría parecer hiperactiva.
Estado run (Corriendo): frame_duration = 0.08 (80 ms)
Justificación: Se usa un tiempo más corto y rápido. Esto hace que los fotogramas de la carrera se sucedan velozmente, dando una sensación de energía, velocidad y fluidez que coincide con la acción de correr.
Estado jump (Salto): frame_duration = 0.10 (100 ms)
Justificación: Un valor intermedio. Permite que los fotogramas de la animación de salto (que tiene 4 frames) sean claros y perceptibles durante el ascenso y descenso, sin ser ni tan lentos como el idle ni tan frenéticos como el run.

Extensiones Implementadas (2+)
Se implementaron exitosamente todas las extensiones solicitadas. Aquí se detallan 3 de las más destacadas:
1. Extensión: Ciclo Día/Noche con Transiciones Suaves (Reto #6)
Explicación: Se creó una clase DayNightManager que gestiona un "reloj" interno (self.time_of_day). Esta clase interpola suavemente (usando lerp_color) entre 4 paletas de colores clave: night, dawn, day y dusk. El resultado se pasa a la función draw_gradient_bg para teñir el cielo en tiempo real, creando un ciclo día/noche automático y visualmente fluido que se repite cada 120 segundos.
2. Extensión: Sistema de Partículas de Polvo (Reto #7)
Explicación: Se implementó un sistema de partículas eficiente usando dos clases: Particle (que gestiona su propia vida, física y encogimiento) y ParticleEmitter (que las genera). En la clase AnimSprite, el método handle_particles revisa si el jugador está corriendo en el suelo. Si es así, emite partículas en la dirección opuesta al movimiento, creando un efecto de polvo realista.
3. Extensión: Carga de Sprite Sheets Externos (Reto #1)
Explicación: En lugar de dibujar los frames del jugador con código (make_idle_frames), se creó una función load_sprite_sheet. Esta función carga un archivo PNG (Biker_idle.png, Biker_run.png, etc.), lo corta en frames individuales usando subsurface() y los almacena en una lista. Esto permite usar arte profesional y cambiar de personaje fácilmente. El código incluye un fallback a los frames generados por código en caso de que las imágenes no se encuentren.
Evidencia:





# P4_Fondos_Animaciones_Rodrigo_Garcia_Gallegos
