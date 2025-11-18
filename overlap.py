import pygame
import math
import sys
import pandas as pd
from datetime import datetime

# Initialize Pygame
pygame.init()

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Circle Overlap Experiment")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
DARK_BLUE = (50, 75, 200)
DARK_RED = (200, 50, 50)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
SLIDER_COLOR = (150, 150, 150)

# Circle parameters
base_radius = 50  # Base radius for left circle
left_circle_pos = (550, 300)  # Fixed position for left circle

# Fixed label positions
LEFT_LABEL_POS = (400, 120)  # Fixed position for left circle label
RIGHT_LABEL_POS = (800, 120)  # Fixed position for right circle label

# Slider class
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, center_val=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.handle_radius = 12
        self.center_val = center_val  # Optional center value for special marking
        
    def get_handle_x(self):
        # Calculate handle position based on current value
        if self.label == "Right Circle Size":
            # Use logarithmic scale for size slider
            log_min = math.log10(self.min_val)
            log_max = math.log10(self.max_val)
            log_value = math.log10(self.value)
            proportion = (log_value - log_min) / (log_max - log_min)
        else:
            # Linear scale for other sliders
            proportion = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + proportion * self.rect.width
    
    def get_center_x(self):
        # Calculate position of center value marker
        if self.center_val is not None:
            if self.label == "Right Circle Size":
                # Use logarithmic scale for size slider
                log_min = math.log10(self.min_val)
                log_max = math.log10(self.max_val)
                log_center = math.log10(self.center_val)
                proportion = (log_center - log_min) / (log_max - log_min)
            else:
                proportion = (self.center_val - self.min_val) / (self.max_val - self.min_val)
            return self.rect.x + proportion * self.rect.width
        return None
    
    def draw(self, screen):
        # Draw slider track
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, border_radius=5)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2, border_radius=5)
        
        # Draw center marker if applicable
        center_x = self.get_center_x()
        if center_x is not None:
            pygame.draw.line(screen, BLACK, (center_x, self.rect.y), (center_x, self.rect.y + self.rect.height), 3)
        
        # Draw filled portion
        handle_x = self.get_handle_x()
        filled_width = handle_x - self.rect.x
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
            pygame.draw.rect(screen, SLIDER_COLOR, filled_rect, border_radius=5)
        
        # Draw handle
        handle_pos = (int(handle_x), self.rect.centery)
        pygame.draw.circle(screen, DARK_BLUE if self.label == "Right Circle Size" else DARK_RED, handle_pos, self.handle_radius)
        pygame.draw.circle(screen, WHITE, handle_pos, self.handle_radius - 3)
        
        # Draw label
        font = pygame.font.Font(None, 28)
        label_text = font.render(self.label, True, BLACK)
        label_rect = label_text.get_rect(center=(self.rect.centerx, self.rect.y - 30))
        screen.blit(label_text, label_rect)
        
        # Draw value
        if self.label != "Right Circle Size":  # Only show value for non-size sliders
            value_text = f"{self.value:.0f}%"
            value_surface = font.render(value_text, True, BLACK)
            value_rect = value_surface.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height + 25))
            screen.blit(value_surface, value_rect)
        
        # Draw tick labels for size slider
        if self.label == "Right Circle Size":
            tick_font = pygame.font.Font(None, 20)
            # Draw labels at key points (using log scale)
            labels = {10: "smaller", 100: "same", 1000: "larger"}
            for val, text in labels.items():
                log_min = math.log10(self.min_val)
                log_max = math.log10(self.max_val)
                log_val = math.log10(val)
                proportion = (log_val - log_min) / (log_max - log_min)
                tick_x = self.rect.x + proportion * self.rect.width
                tick_label = tick_font.render(text, True, DARK_GRAY)
                tick_rect = tick_label.get_rect(center=(tick_x, self.rect.y - 10))
                screen.blit(tick_label, tick_rect)
        
        # Draw tick labels for overlap slider
        elif self.label == "Overlap Percentage":
            tick_font = pygame.font.Font(None, 22)
            # Draw 0% at left end and 100% at right end
            for val in [0, 100]:
                proportion = (val - self.min_val) / (self.max_val - self.min_val)
                tick_x = self.rect.x + proportion * self.rect.width
                tick_label = tick_font.render(f"{val}%", True, BLACK)
                tick_rect = tick_label.get_rect(center=(tick_x, self.rect.y - 12))
                screen.blit(tick_label, tick_rect)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        handle_x = self.get_handle_x()
        handle_pos = (handle_x, self.rect.centery)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on handle or track
            distance = math.sqrt((mouse_pos[0] - handle_pos[0])**2 + (mouse_pos[1] - handle_pos[1])**2)
            if distance <= self.handle_radius or self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.update_value(mouse_pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(mouse_pos[0])
    
    def update_value(self, mouse_x):
        # Clamp mouse position to slider bounds
        mouse_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
        
        # Calculate value based on position
        proportion = (mouse_x - self.rect.x) / self.rect.width
        
        # Use logarithmic scale for size slider to make 100% appear at midpoint
        if self.label == "Right Circle Size":
            # Map proportion to logarithmic scale
            # At proportion=0.5, we want value=100
            # At proportion=0, value=10
            # At proportion=1, value=1000
            # Using log scale: log(10) to log(1000), with log(100) at midpoint
            log_min = math.log10(self.min_val)  # log(10) = 1
            log_max = math.log10(self.max_val)  # log(1000) = 3
            log_value = log_min + proportion * (log_max - log_min)
            self.value = 10 ** log_value
        else:
            # Linear scale for overlap slider
            self.value = self.min_val + proportion * (self.max_val - self.min_val)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, screen):
        # Choose color based on hover state
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw button
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=8)
        
        # Draw text
        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False


def draw_circle_with_outline(screen, center, radius, fill_color, outline_color, alpha=180):
    """Draw a circle with transparency"""
    # Create a surface with per-pixel alpha
    surface = pygame.Surface((int(radius * 2 + 10), int(radius * 2 + 10)), pygame.SRCALPHA)
    
    # Draw filled circle with transparency
    local_center = (int(radius + 5), int(radius + 5))
    pygame.draw.circle(surface, (*fill_color, alpha), local_center, int(radius))
    
    # Draw outline
    pygame.draw.circle(surface, outline_color, local_center, int(radius), 3)
    
    # Blit to screen
    screen.blit(surface, (center[0] - radius - 5, center[1] - radius - 5))


def calculate_right_circle_position(overlap_percent, left_radius, right_radius, left_x):
    """
    Calculate the x-position of the right circle to achieve the desired overlap.
    """
    if overlap_percent == 0:
        # No overlap: circles just touch
        separation = left_radius + right_radius
    else:
        # Calculate overlap distance
        max_overlap = min(left_radius, right_radius) * 2
        actual_overlap = (overlap_percent / 100.0) * max_overlap
        
        # Separation is the sum of radii minus the overlap distance
        separation = left_radius + right_radius - actual_overlap
    
    # Right circle position
    right_center_x = left_x + separation
    
    return right_center_x


# Read the CSV file with label pairs
try:
    df = pd.read_csv('labels.csv')  # Change this to your CSV file path
    if 'label1' not in df.columns or 'label2' not in df.columns:
        print("Error: CSV must contain 'label1' and 'label2' columns")
        sys.exit(1)
except FileNotFoundError:
    print("Error: labels.csv not found. Please provide a CSV file with 'label1' and 'label2' columns")
    sys.exit(1)

# Participant ID input screen
participant_id = ""
input_active = True
clock = pygame.time.Clock()

# Fonts for input screen
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

while input_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and participant_id:
                # Enter pressed and ID is not empty
                input_active = False
            elif event.key == pygame.K_BACKSPACE:
                # Remove last character
                participant_id = participant_id[:-1]
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            else:
                # Add character (limit to 20 characters)
                if len(participant_id) < 20 and event.unicode.isprintable():
                    participant_id += event.unicode
    
    # Draw input screen
    screen.fill(WHITE)
    
    # Title
    title = font_large.render("Circle Overlap Experiment", True, BLACK)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
    screen.blit(title, title_rect)
    
    # Instructions
    instruction1 = font_medium.render("Please enter your Participant ID:", True, BLACK)
    instruction1_rect = instruction1.get_rect(center=(WINDOW_WIDTH // 2, 300))
    screen.blit(instruction1, instruction1_rect)
    
    # Input box
    input_box = pygame.Rect(WINDOW_WIDTH // 2 - 200, 360, 400, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, input_box)
    pygame.draw.rect(screen, BLACK, input_box, 3)
    
    # Display typed text
    text_surface = font_medium.render(participant_id, True, BLACK)
    text_rect = text_surface.get_rect(center=input_box.center)
    screen.blit(text_surface, text_rect)
    
    # Cursor (blinking)
    if int(pygame.time.get_ticks() / 500) % 2 == 0:
        cursor_x = text_rect.right + 5
        cursor_y = input_box.centery
        pygame.draw.line(screen, BLACK, (cursor_x, cursor_y - 15), (cursor_x, cursor_y + 15), 2)
    
    # Instructions for submission
    instruction2 = font_small.render("Press ENTER to continue", True, DARK_GRAY)
    instruction2_rect = instruction2.get_rect(center=(WINDOW_WIDTH // 2, 450))
    screen.blit(instruction2, instruction2_rect)
    
    pygame.display.flip()
    clock.tick(60)

# Data collection list
results = []

# Create sliders with updated range (10% to 1000%, centered at 100% using log scale)
size_slider = Slider(300, 550, 600, 30, 10, 1000, 100, "Right Circle Size", center_val=100)
overlap_slider = Slider(300, 650, 600, 30, 0, 100, 0, "Overlap Percentage")

# Create Next button
next_button = Button(1050, 720, 120, 50, "Next", LIGHT_GRAY, SLIDER_COLOR, BLACK)

# Main loop
clock = pygame.time.Clock()
running = True

# Instructions
font_title = pygame.font.Font(None, 32)
font_instructions = pygame.font.Font(None, 24)

# Trial tracking
current_trial = 0
total_trials = len(df)

while running and current_trial < total_trials:
    # Get current labels
    label1 = df.iloc[current_trial]['label1']
    label2 = df.iloc[current_trial]['label2']
    
    # Trial loop
    trial_running = True
    while trial_running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                trial_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    trial_running = False
            
            # Pass events to sliders
            size_slider.handle_event(event)
            overlap_slider.handle_event(event)
            
            # Check if Next button clicked
            if next_button.handle_event(event):
                # Save current trial data
                size_percent = size_slider.value
                overlap_percent = overlap_slider.value
                
                results.append({
                    'participant_id': participant_id,
                    'trial': current_trial + 1,
                    'label1': label1,
                    'label2': label2,
                    'size_percent': size_percent,
                    'overlap_percent': overlap_percent,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # Reset sliders for next trial
                size_slider.value = 100
                overlap_slider.value = 0
                
                # Move to next trial
                current_trial += 1
                trial_running = False
        
        if not trial_running:
            break
        
        # Clear screen
        screen.fill(WHITE)
        
        # Get slider values
        size_percent = size_slider.value
        overlap_percent = overlap_slider.value
        
        # Calculate right circle radius based on size (area-based)
        size_ratio = size_percent / 100.0
        right_radius = base_radius * math.sqrt(size_ratio)
        
        # Calculate right circle position
        right_x = calculate_right_circle_position(overlap_percent, base_radius, right_radius, left_circle_pos[0])
        right_circle_pos = (right_x, left_circle_pos[1])
        
        # Draw title and trial progress
        title = font_title.render("Circle Overlap Experiment", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 40))
        screen.blit(title, title_rect)
        
        progress = font_instructions.render(f"Trial {current_trial + 1} of {total_trials}", True, DARK_GRAY)
        progress_rect = progress.get_rect(center=(WINDOW_WIDTH // 2, 75))
        screen.blit(progress, progress_rect)
        
        # Draw circles (right circle first so left appears on top when overlapping)
        draw_circle_with_outline(screen, right_circle_pos, right_radius, RED, DARK_RED)
        draw_circle_with_outline(screen, left_circle_pos, base_radius, BLUE, DARK_BLUE)
        
        # Draw circle labels at fixed positions with current trial labels
        left_label = font_instructions.render(str(label1), True, DARK_BLUE)
        left_label_rect = left_label.get_rect(center=LEFT_LABEL_POS)
        screen.blit(left_label, left_label_rect)
        
        right_label = font_instructions.render(str(label2), True, DARK_RED)
        right_label_rect = right_label.get_rect(center=RIGHT_LABEL_POS)
        screen.blit(right_label, right_label_rect)
        
        # Draw sliders
        size_slider.draw(screen)
        overlap_slider.draw(screen)
        
        # Draw Next button
        next_button.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)  # 60 FPS for smooth animation

# Save results to CSV
if results:
    output_filename = f'overlap_results_{participant_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_filename, index=False)
    print(f"\nResults saved to {output_filename}")
    print(f"Total trials completed: {len(results)}")
else:
    print("\nNo data collected")

# Quit
pygame.quit()
sys.exit()