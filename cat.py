import pygame
import random
import json
from pygame.locals import *
from pyllist import dllist

# Initialize pygame
pygame.init()

# Display settings
WIDTH = 780  
HEIGHT = 550  

screen = pygame.display.set_mode((WIDTH, HEIGHT))


background_image = pygame.image.load('C:\\Users\\pawlo\\OneDrive\\Desktop\\sd2\\background.jpg')
screen.blit(background_image, (0, 0))
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# CARDS graphics
CARD_WIDTH, CARD_HEIGHT = 100, 150
card_placeholder = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
card_placeholder.fill((255, 255, 255))

class Card:
    def __init__(self, name, card_type, effect_value, image_path):
        self.name = name
        self.type = card_type
        self.effect_value = effect_value
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

class Node:
    def __init__(self, card=None):
        self.card = card
        self.prev = None
        self.next = None

class CircularDoublyLinkedList(dllist):
    def append(self, value):
        super().append(value)
        if self.first is not None and self.size > 1:
            self.first.prev = self.last
            self.last.next = self.first

    def remove(self, node):
        super().remove(node)
        if self.first is not None and self.size > 1:
            self.first.prev = self.last
            self.last.next = self.first

    def __len__(self):
        return self.size



class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 50
        self.hand = dllist()
        self.current_card = None  
        self.last_played_card = None
        self.update_last_card = False
      
    def draw_cards(self, deck):
        while len(self.hand) < 5 and deck:
            card = deck.pop(random.randint(0, len(deck) - 1))
            self.hand.append(card)
        if not deck:
            deck.extend(Game.generate_cards())
        if self.current_card is None and len(self.hand) > 0:
            self.current_card = self.hand.first

    def display_hand(self, surface):
        x_offset = 20
        font = pygame.font.SysFont(None, 18)  
        for node in self.hand.iternodes():  # Iterate over nodes of the list
            card = node.value  # Access the card using the 'value' attribute of the node
            pygame.draw.rect(surface, (255, 255, 255), (x_offset, HEIGHT - CARD_HEIGHT - 10, CARD_WIDTH, CARD_HEIGHT), 2)  
            surface.blit(card.image, (x_offset, HEIGHT - CARD_HEIGHT - 10))  
            card_text = font.render(card.name, True, BLACK)
            text_rect = card_text.get_rect(center=(x_offset + CARD_WIDTH/2, HEIGHT - CARD_HEIGHT/2 - 5))
            surface.blit(card_text, text_rect)
            if card.type in ["damage", "heal"]:
                effect_text = font.render(str(card.effect_value), True, BLACK)
                effect_rect = effect_text.get_rect(center=(x_offset + CARD_WIDTH/2, HEIGHT - CARD_HEIGHT/2 + 20))
                surface.blit(effect_text, effect_rect)
            x_offset += CARD_WIDTH + 20
    
    #def apply_effects(self):
       ##     self.effects["reduce_damage"] = False
       # if self.effects.get("reverse_damage"):
       #     self.effects["reverse_damage"] = False
    
    def play_card(self, node, opponent):
        card = node.value
        self.hand.remove(node)
        self.last_played_card = card
        self.update_last_card = True
        
        if card.type == "damage":
            damage = card.effect_value
            opponent.hp -= damage
        elif card.type == "heal":
            self.hp += card.effect_value
            self.hp = min(self.hp, 50)
        if self.current_card is None and len(self.hand) > 0:
            self.current_card = self.hand.first

    def next_card(self):
        # Logic to navigate to the next card
        if self.current_card is None and len(self.hand) > 0:
            self.current_card = self.hand.first
        elif self.current_card.next is not None:
            self.current_card = self.current_card.next
        else:
            self.current_card = self.hand.first  # Wrap around to the first card
    
    def previous_card(self):
        # Logic to navigate to the previous card
        if self.current_card is None and len(self.hand) > 0:
            self.current_card = self.hand.last
        elif self.current_card.prev is not None:
            self.current_card = self.current_card.prev
        else:
            self.current_card = self.hand.last  # Wrap around to the last card
    
    def draw_three_cards(self, deck):
        for _ in range(3):  # Draw three cards
            if deck:
                card = deck.pop(random.randint(0, len(deck) - 1))
                self.hand.append(card)
            if not deck:  # If the deck is empty, generate new cards
                deck.extend(Game.generate_cards())

    def discard_random_card(self):
        if len(self.hand) > 0:
            # Generate a random index
            random_index = random.randint(0, len(self.hand) - 1)
            # Find the node at the random index
            current_node = self.hand.first  # Use 'first' instead of 'head'
            for _ in range(random_index):
                current_node = current_node.next
            # Remove the selected card
            self.hand.remove(current_node)

    def check_card_clicked(self, mouse_pos):
        x_offset = 20
        for node in self.hand.iternodes():  
            card = node.value 
            if (x_offset <= mouse_pos[0] <= x_offset + CARD_WIDTH and 
                HEIGHT - CARD_HEIGHT - 10 <= mouse_pos[1] <= HEIGHT - 10):
                return node
            x_offset += CARD_WIDTH + 20
        return None
    
    def display_hp(self, surface, position):
        font = pygame.font.SysFont(None, 35)
        hp_text = font.render(f"{self.name} HP: {self.hp}", True, (0, 255,0))
        surface.blit(hp_text, position)

    def discard_random_card(self):
        if len(self.hand) > 0:
            # Generate a random index
            random_index = random.randint(0, len(self.hand) - 1)
            # Find the node at the random index
            current_node = self.hand.first  # Use 'first' instead of 'head'
            for _ in range(random_index):
                current_node = current_node.next
            # Remove the selected card
            self.hand.remove(current_node)

class Game:
    def __init__(self):
        self.cat = Player("Cat")
        self.dog = Player("Dog")
        self.deck = self.generate_cards()

    @staticmethod
    def generate_cards():
        with open('cards.json', 'r') as file:
            card_data = json.load(file)
        return [Card(card['name'], card['type'], card['value'], card['image_path']) for card in card_data]
    
    def player_turn(self, player, opponent):
        """Handle a player's turn."""
        player.draw_three_cards(self.deck)

        # Choose a random node (not just the card) to play
        if len(player.hand) > 0:
            random_index = random.randint(0, len(player.hand) - 1)
            node_to_play = player.hand.nodeat(random_index)  # Get the node at random_index
            player.play_card(node_to_play, opponent)  # Pass the node, not the card

        # Each player discards a random card
        player.discard_random_card()

game = Game()
game.cat.draw_cards(game.deck)
game.dog.draw_cards(game.deck)
current_player = game.cat

run = True
while run:
    screen.fill(BLACK)
    screen.blit(background_image, (0, 0))

    # Display player's hand and HP
    game.cat.display_hand(screen)
    game.dog.display_hp(screen, (10, 10))
    game.cat.display_hp(screen, (WIDTH - 130, 10))

    # Display the opponent's last played card if the flag is set
    if game.dog.update_last_card:
        opponent_last_card = game.dog.last_played_card
        if opponent_last_card:
            card_image = pygame.transform.scale(opponent_last_card.image, (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(card_image, (WIDTH // 2 - CARD_WIDTH // 2, HEIGHT // 2 - CARD_HEIGHT // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == MOUSEBUTTONDOWN and current_player == game.cat:
            clicked_node = game.cat.check_card_clicked(pygame.mouse.get_pos())
            if clicked_node is not None:
                game.cat.play_card(clicked_node, game.dog)
                game.dog.update_last_card = False  # Reset the flag after the player plays a card
                game.player_turn(game.cat, game.dog)
                game.player_turn(game.dog, game.cat)

        if game.cat.hp <= 0 or game.dog.hp <= 0:
            run = False

    pygame.display.flip()


if game.cat.hp <= 0:
    winner = "Dog"
elif game.dog.hp <= 0:
    winner = "Cat"
else:
    winner = None

# Display the win/lose message
font = pygame.font.SysFont(None, 74)
if winner:
    win_text = font.render(f"{winner} Wins!", True, (0, 255, 0))
else:
    win_text = font.render("It's a Draw!", True, (0, 255, 0))

text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
screen.blit(win_text, text_rect)
pygame.display.flip()

# Pause to display the win/lose message
pygame.time.wait(3000)
pygame.quit()