import pygame
import numpy as np
import sys
import math

# === USER INPUT ===
def get_input(prompt, default, cast):
    try:
        return cast(input(f"{prompt} (default={default}): ") or default)
    except:
        print(f"Invalid input. Using default: {default}")
        return cast(default)

# Wormhole shape parameters
bridge_radius = get_input("Throat radius", 50, float)
bridge_scale = get_input("Bridge height scale", 1.5, float)  # Elongated vertically
num_rings = get_input("Number of cross-section slices", 150, int)
resolution = get_input("Points per ring (angular resolution)", 80, int)

# === INIT PYGAME ===
pygame.init()
width, height = 1920, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Einstein-Rosen Bridge Simulation")
clock = pygame.time.Clock()

zoom = 5
rotation = 0
running = True
time = 0
rotation_default = 0.0075
rotation_velocity = rotation_default
mouse_interacting = False
mouse_last_x = 0
last_mouse_time = pygame.time.get_ticks()
return_delay = 1000  # milliseconds before auto-spin resumes


def clamp(val, minval=0, maxval=255):
    return max(minval, min(int(val), maxval))

# 3D to 2D projection for side view
def project_3d(x, y, z, angle):
    # Rotate around Y axis (to simulate turning the shape)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x_rot = x * cos_a - z * sin_a
    z_rot = x * sin_a + z * cos_a

    # Perspective projection
    fov = 500
    scale = fov / (fov + z_rot + 200)  # Shift forward to keep in front of camera
    px = int(x_rot * scale * zoom + width // 2)
    py = int(y * scale * zoom + height // 2)
    return (px, py)

# Main loop
while running:
    screen.fill((5, 5, 15))
    time += 0.02

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            zoom += event.y * 0.5
            zoom = max(1, min(20, zoom))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_interacting = True
                mouse_last_x = pygame.mouse.get_pos()[0]
                last_mouse_time = pygame.time.get_ticks()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_interacting = False
                last_mouse_time = pygame.time.get_ticks()

    current_time = pygame.time.get_ticks()

    # Manual spin with mouse drag and inertia
    if mouse_interacting:
        mouse_x = pygame.mouse.get_pos()[0]
        dx = mouse_x - mouse_last_x
        rotation_velocity = dx * 0.005  # store current drag as velocity
        rotation += rotation_velocity
        mouse_last_x = mouse_x
    else:
        # Apply stored velocity with decay
        rotation += rotation_velocity
        rotation_velocity *= 0.98  # inertia decay

        # If enough time passed without interaction, return to default spin
        if current_time - last_mouse_time > return_delay:
            # Gradually ease toward default rotation
            rotation_velocity += (rotation_default - rotation_velocity) * 0.01

    # Draw rings
    for i in range(-num_rings//2, num_rings//2):
        # Modify the shape to compress the ends and elongate the center
        normalized_z = i / (num_rings / 2)
        squeeze = 1 - math.exp(-abs(normalized_z) * 3)  # more squeeze at the ends
        z = i * bridge_scale
        r = math.sqrt(bridge_radius ** 2 + (z * (0.5 + 0.5 * squeeze)) ** 2)

        # Generate ring points
        ring_points = []
        for j in range(resolution):
            theta = 2 * math.pi * j / resolution
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            px, py = project_3d(x, y, z, rotation)
            ring_points.append((px, py))

        # Blue-Grey Shades
        depth = abs(i) / num_rings
        blue = 255
        green = clamp(180 + 50 * math.sin(time + i * 0.5))  # Subtle flicker in green
        red = clamp(120 + 50 * math.sin(time + i * 0.3))  # Light bluish-grey hue
        color = (red, green, blue)

        # Draw ring
        for k in range(len(ring_points)):
            pygame.draw.line(screen, color, ring_points[k], ring_points[(k + 1) % len(ring_points)], 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
