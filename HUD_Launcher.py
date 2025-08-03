import subprocess
import pygame
pygame.init()


fenetre = pygame.display.set_mode((500, 350), pygame.DOUBLEBUF, pygame.HWSURFACE)
pygame.display.set_caption("Elite HUD launcher")


sys_process = None
joystick_process = None
exobio_process = None
stats_process = None


def lancer_systeme():
    global sys_process
    sys_process = subprocess.Popen(["python", "HUD_System.py"])

def arreter_systeme():
    global sys_process
    if sys_process and sys_process.poll() is None:
        sys_process.terminate() # ou .kill() si inefficace
        sys_process = None


def lancer_exobio(HUD_Systeme_running):
    global exobio_process
    
    decalerFenetreExobio = "False"
    if HUD_Systeme_running:
        decalerFenetreExobio = "True"
    else:
        decalerFenetreExobio = "False"
        
    exobio_process = subprocess.Popen(["python", "HUD_ExoBio.py", decalerFenetreExobio])

def arreter_exobio():
    global exobio_process
    if exobio_process and exobio_process.poll() is None:
        exobio_process.terminate() # ou .kill() si inefficace
        exobio_process = None


def lancer_stats():
    global stats_process
    stats_process = subprocess.Popen(["python", "HUD_SessionStats.py"])

def arreter_stats():
    global stats_process
    if stats_process and stats_process.poll() is None:
        stats_process.terminate() # ou .kill() si inefficace
        stats_process = None


def run():
    HUD_Systeme_running = False
    HUD_Stats_running = False
    HUD_Combat_running = False
    HUD_ExoBio_running = False
    
    police1 = pygame.font.Font(None, 30)

    # Variables pour les couleurs de survol
    COLOR1 = (0, 150, 100)
    COLOR2 = (180, 0, 0)
    COLOR3 = (0, 100, 255)
    WHITE = (255, 255, 255)

    button1_x = 50
    button1_y = 50
    button1_width = 150
    button1_height = 50
    button1_color = COLOR1
    button1_text = "Systems"

    button2_x = 300
    button2_y = 50
    button2_width = 150
    button2_height = 50
    button2_color = COLOR1
    button2_text = "ExoBio"

    button3_x = 50
    button3_y = 150
    button3_width = 150
    button3_height = 50
    button3_color = COLOR1
    button3_text = "Fighting"
    
    button4_x = 300
    button4_y = 150
    button4_width = 150
    button4_height = 50
    button4_color = COLOR1
    button4_text = "Stats"

    button1_rect = pygame.Rect(button1_x, button1_y, button1_width, button1_height)
    button2_rect = pygame.Rect(button2_x, button2_y, button2_width, button2_height)
    button3_rect = pygame.Rect(button3_x, button3_y, button3_width, button3_height)
    button4_rect = pygame.Rect(button4_x, button4_y, button4_width, button4_height)

    texte_1 = police1.render(button1_text, True, WHITE)
    texte_2 = police1.render(button2_text, True, WHITE)
    texte_3 = police1.render(button3_text, True, WHITE)
    texte_4 = police1.render(button4_text, True, WHITE)

    texte_1_rect = texte_1.get_rect(center=(button1_rect.centerx, button1_rect.centery))
    texte_2_rect = texte_2.get_rect(center=(button2_rect.centerx, button2_rect.centery))
    texte_3_rect = texte_3.get_rect(center=(button3_rect.centerx, button3_rect.centery))
    texte_4_rect = texte_4.get_rect(center=(button4_rect.centerx, button4_rect.centery))
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEMOTION:
                # Position de la souris
                x, y = pygame.mouse.get_pos()
            
                # Vérification de la position de la souris pour mettre à jour la couleur des boutons
                if button1_x <= x <= (button1_x + button1_width) and button1_y <= y <= (button1_y + button1_height):
                    button1_color = COLOR3
                elif HUD_Systeme_running:
                    button1_color = COLOR2
                else:
                    button1_color = COLOR1

                if button2_x <= x <= (button2_x + button2_width) and button2_y <= y <= (button2_y + button2_height):
                    button2_color = COLOR3
                elif HUD_ExoBio_running:
                    button2_color = COLOR2
                else:
                    button2_color = COLOR1

                if button3_x <= x <= (button3_x + button3_width) and button3_y <= y <= (button3_y + button3_height):
                    button3_color = COLOR3
                elif HUD_Combat_running:
                    button3_color = COLOR2
                else:
                    button3_color = COLOR1
                    
                if button4_x <= x <= (button4_x + button4_width) and button4_y <= y <= (button4_y + button4_height):
                    button4_color = COLOR3
                elif HUD_Stats_running:
                    button4_color = COLOR2
                else:
                    button4_color = COLOR1
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Gestion du clic sur les boutons
                if button1_x <= x <= (button1_x + button1_width) and button1_y <= y <= (button1_y + button1_height) and not HUD_Systeme_running:
                    print("Button 1 clicked")
                    # Executer un le fichier HUD_Systemev5.py dans un thread séparé
                    lancer_systeme()
                    HUD_Systeme_running = True
                    
                elif button1_x <= x <= (button1_x + button1_width) and button1_y <= y <= (button1_y + button1_height) and HUD_Systeme_running:
                    print("Button 1 already running, stopping it")
                    arreter_systeme()
                    HUD_Systeme_running = False
                    
                
                if button2_x <= x <= (button2_x + button2_width) and button2_y <= y <= (button2_y + button2_height) and not HUD_ExoBio_running:
                    print("Button 2 clicked")
                    # Executer un le fichier HUD_Joystickv8.py dans un thread séparé
                    lancer_exobio(HUD_Systeme_running)
                    HUD_ExoBio_running = True
                    
                elif button2_x <= x <= (button2_x + button2_width) and button2_y <= y <= (button2_y + button2_height) and HUD_ExoBio_running:
                    print("Button 2 already running, stopping it")
                    arreter_exobio()
                    HUD_ExoBio_running = False
                    
                
                if button3_x <= x <= (button3_x + button3_width) and button3_y <= y <= (button3_y + button3_height) and not HUD_Combat_running:
                    print("Button 3 clicked")
                    HUD_Combat_running = True
                    
                elif button3_x <= x <= (button3_x + button3_width) and button3_y <= y <= (button3_y + button3_height) and HUD_Combat_running:
                    print("Button 3 already running, stopping it")
                    HUD_Combat_running = False
                    
                
                if button4_x <= x <= (button4_x + button4_width) and button4_y <= y <= (button4_y + button4_height) and not HUD_Stats_running:
                    print("Button 4 clicked")
                    lancer_stats()
                    HUD_Stats_running = True
                    
                elif button4_x <= x <= (button4_x + button4_width) and button4_y <= y <= (button4_y + button4_height) and HUD_Stats_running:
                    print("Button 4 already running, stopping it")
                    arreter_stats()
                    HUD_Stats_running = False
                    
        
        fenetre.fill((0, 0, 0)) # Fond noir

        # Dessiner les boutons
        pygame.draw.rect(fenetre, button1_color, button1_rect)
        pygame.draw.rect(fenetre, button2_color, button2_rect)
        pygame.draw.rect(fenetre, button3_color, button3_rect)
        pygame.draw.rect(fenetre, button4_color, button4_rect)

        fenetre.blit(texte_1, texte_1_rect)
        fenetre.blit(texte_2, texte_2_rect)
        fenetre.blit(texte_3, texte_3_rect)
        fenetre.blit(texte_4, texte_4_rect)

        pygame.display.flip()

run()
pygame.quit()