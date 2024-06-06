from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
import random

contrade = [
    'Aquila', 'Bruco', 'Chiocciola', 'Civetta', 'Drago',
    'Giraffa', 'Istrice', 'Leocorno', 'Lupa', 'Nicchio',
    'Oca', 'Onda', 'Pantera', 'Selva', 'Tartuca', 'Torre', 'Valdimontone'
]

cavalli = [
    'Occolè', 'Aramis', 'Sarò', 'Bellino', 'Margò',
    'Pathos', 'Rondone', 'Tiramisù', 'Zaù', 'Zorba',
    'Fulmine', 'Saetta', 'Lampo', 'Tempesta', 'Vento',
    'Tuono', 'Folgore'
]

class MyGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.opacity = 0.8

        self.add_widget(Label(text='IL PALIO DI SIENA', font_size='24sp', size_hint=(1, 0.1), opacity=0.8))

        self.add_widget(Label(text='Seleziona la tua contrada:', opacity=0.8))

        self.contrada_spinner = Spinner(
            text=contrade[0],
            values=contrade,
            opacity=0.8
        )
        self.add_widget(self.contrada_spinner)

        self.add_widget(Label(text='Seleziona il tuo cavallo:', opacity=0.8))

        self.cavallo_spinner = Spinner(
            text=cavalli[0],
            values=cavalli,
            opacity=0.8
        )
        self.add_widget(self.cavallo_spinner)

        self.start_button = Button(text='Inizia il Gioco', opacity=0.8)
        self.start_button.bind(on_press=self.start_game)
        self.add_widget(self.start_button)

    def start_game(self, instance):
        self.contrada = self.contrada_spinner.text
        self.cavallo = self.cavallo_spinner.text
        self.race = RaceScreen(self.contrada, self.cavallo)
        self.clear_widgets()
        self.add_widget(self.race)

class RaceScreen(BoxLayout):
    deck_special = []
    deck_movement = []
    discard_pile_special = []
    discard_pile_movement = []

    def __init__(self, contrada, cavallo, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.contrada = contrada
        self.cavallo = cavallo
        self.tappe = 16
        self.current_tappa = 1
        self.positions = {contrada: 0}
        self.horses = {contrada: cavallo}
        self.used_cards = {contrada: ''}  # Memorizza le carte usate
        self.movement_cards = {contrada: ''}  # Memorizza le carte movimento usate
        self.special_disabled = {contrada: False}  # Disabilita carte speciali
        self.movement_hands = {}
        self.special_hands = {}
        other_contrade = random.sample([c for c in contrade if c != contrada], 9)
        other_cavalli = random.sample(cavalli, 9)
        for i in range(9):
            self.positions[other_contrade[i]] = 0
            self.horses[other_contrade[i]] = other_cavalli[i]
            self.used_cards[other_contrade[i]] = ''
            self.movement_cards[other_contrade[i]] = ''
            self.special_disabled[other_contrade[i]] = False

        self.create_decks()
        random.shuffle(RaceScreen.deck_special)
        random.shuffle(RaceScreen.deck_movement)

        # Deal hands to players and AI
        self.hand_special = [RaceScreen.deck_special.pop() for _ in range(3)]
        self.hand_movement = [RaceScreen.deck_movement.pop() for _ in range(3)]
        for contrada in self.positions:
            self.movement_hands[contrada] = [RaceScreen.deck_movement.pop() for _ in range(3)]
            self.special_hands[contrada] = [RaceScreen.deck_special.pop() for _ in range(3)]

        self.create_race_ui()
        self.advance_turn()  # Ensure the AI plays the first turn

    def create_decks(self):
        # Resetting decks and discard pile
        RaceScreen.deck_special = ['sprona_1'] * 80 + ['nerbata_-1'] * 80 + ['sprona_3'] * 20 + ['nerbata_-3'] * 20 + ['sgambetto'] * 2
        RaceScreen.deck_movement = [str(i) for i in range(2, 7)] * 40
        RaceScreen.discard_pile_special = []
        RaceScreen.discard_pile_movement = []

    def create_race_ui(self):
        # Top layout with the current stage
        top_layout = BoxLayout(size_hint=(1, 0.1))
        self.label = Label(text=f'Tappa {self.current_tappa} di {self.tappe}', font_size='24sp', opacity=1)
        top_layout.add_widget(self.label)
        self.add_widget(top_layout)

        # Race status scroll view
        self.race_status = ScrollView(size_hint=(1, None), size=(self.width, 400))
        self.race_status_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.race_status_layout.bind(minimum_height=self.race_status_layout.setter('height'))
        self.race_status.add_widget(self.race_status_layout)
        self.add_widget(self.race_status)

        self.update_race_status()

        # Layout for movement cards
        self.card_layout_movement = GridLayout(cols=3, size_hint_y=None, height=50)
        self.card_buttons_movement = []
        for i, card in enumerate(self.hand_movement):
            btn = Button(text=card, background_color=(1, 1, 1, 0.8))
            btn.bind(on_press=self.select_movement_card(i))
            self.card_buttons_movement.append(btn)
            self.card_layout_movement.add_widget(btn)
        self.add_widget(self.card_layout_movement)

        # Layout for special cards
        self.card_layout_special = GridLayout(cols=3, size_hint_y=None, height=50)
        self.card_buttons_special = []
        for i, card in enumerate(self.hand_special):
            btn = Button(text=card.replace('_', ' ').capitalize(), background_color=(1, 1, 1, 0.8))
            if self.special_disabled[self.contrada]:
                btn.disabled = True
            btn.bind(on_press=self.select_special_card(i))
            self.set_button_color(btn, card)
            self.card_buttons_special.append(btn)
            self.card_layout_special.add_widget(btn)
        self.add_widget(self.card_layout_special)

        # Play cards button
        self.play_button = Button(text='Gioca le carte', size_hint=(1, 0.2), background_color=(1, 1, 1, 0.8))
        self.play_button.bind(on_press=self.play_cards)
        self.add_widget(self.play_button)

    def set_button_color(self, button, card):
        if card == 'sprona_1':
            button.background_color = (0, 1, 1, 0.8)  # Celeste
        elif card == 'nerbata_-1':
            button.background_color = (1, 0.65, 0, 0.8)  # Arancione
        elif card == 'sprona_3':
            button.background_color = (0, 1, 0, 0.8)  # Verde
        elif card == 'nerbata_-3':
            button.background_color = (1, 0, 0, 0.8)  # Rosso
        elif card == 'sgambetto':
            button.background_color = (0.5, 0, 0.5, 0.8)  # Viola

    def get_race_status(self):
        status = []
        sorted_positions = sorted(self.positions.items(), key=lambda item: item[1], reverse=True)
        for pos, (contrada, score) in enumerate(sorted_positions, 1):
            flag = Image(source=f'images/{contrada}.png', size_hint=(None, None), size=(30, 30))
            card_used = self.used_cards[contrada]
            movement_card_used = self.movement_cards[contrada]
            if self.special_disabled[contrada]:
                text = f'[color=800080]{pos}. {contrada} (Cavallo: {self.horses[contrada]}): {score} (Movimento: {movement_card_used}) [{card_used}][/color]'
            else:
                text = f'{pos}. {contrada} (Cavallo: {self.horses[contrada]}): {score} (Movimento: {movement_card_used}) [{card_used}]'
            if contrada == self.contrada:
                text = f'[color=ffff00][b]{text}[/b][/color]'
            status.append((flag, text))
        return status

    def update_race_status(self):
        self.label.text = f'Tappa {self.current_tappa} di {self.tappe}'
        self.race_status_layout.clear_widgets()
        race_status = self.get_race_status()
        for flag, line in race_status:
            layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            layout.add_widget(flag)
            label = Label(text=line, markup=True, size_hint_y=None, height=30, opacity=1)
            layout.add_widget(label)
            self.race_status_layout.add_widget(layout)
        if self.current_tappa >= self.tappe:
            self.end_race()

    def select_movement_card(self, index):
        def inner(instance):
            self.selected_movement_card = self.hand_movement[index]
            for btn in self.card_buttons_movement:
                btn.background_color = (1, 1, 1, 0.8)
            instance.background_color = (0.5, 0.5, 0.5, 0.8)
        return inner

    def select_special_card(self, index):
        def inner(instance):
            self.selected_special_card = self.hand_special[index]
            for btn in self.card_buttons_special:
                btn.background_color = (1, 1, 1, 0.8)
            instance.background_color = (0.5, 0.5, 0.5, 0.8)
        return inner

    def play_cards(self, instance):
        if not hasattr(self, 'selected_movement_card') or self.selected_movement_card is None:
            popup = Popup(title='Errore', content=Label(text='Devi selezionare una carta numero.'), size_hint=(0.6, 0.4))
            popup.open()
            return

        if hasattr(self, 'selected_movement_card') and self.selected_movement_card is not None:
            movement_points = int(self.selected_movement_card)
            self.positions[self.contrada] += movement_points
            self.movement_cards[self.contrada] = self.selected_movement_card
            RaceScreen.discard_pile_movement.append(self.selected_movement_card)
            self.hand_movement[self.hand_movement.index(self.selected_movement_card)] = None

        if hasattr(self, 'selected_special_card') and self.selected_special_card is not None:
            card = self.selected_special_card
            if 'sprona' in card:
                points = int(card.split('_')[1])
                self.positions[self.contrada] += points
            elif 'nerbata' in card:
                points = int(card.split('_')[1])
                for contrada, pos in sorted(self.positions.items(), key=lambda item: item[1], reverse=True):
                    if contrada != self.contrada:
                        self.positions[contrada] -= points
                        break
            elif 'sgambetto' in card:
                for contrada, pos in sorted(self.positions.items(), key=lambda item: item[1], reverse=True):
                    if contrada != self.contrada and pos > self.positions[self.contrada]:
                        self.special_disabled[contrada] = True
                        break
            RaceScreen.discard_pile_special.append(card)
            self.used_cards[self.contrada] = card.replace('_', ' ').capitalize()
            self.hand_special[self.hand_special.index(self.selected_special_card)] = None

        # Reset the button colors after playing the cards
        for btn in self.card_buttons_movement:
            btn.background_color = (1, 1, 1, 0.8)
        for btn in self.card_buttons_special:
            btn.background_color = (1, 1, 1, 0.8)

        self.selected_movement_card = None
        self.selected_special_card = None
        self.update_race_status()
        self.current_tappa += 1
        self.advance_turn()
        self.draw_new_cards()

    def advance_turn(self):
        for contrada in self.positions:
            if contrada != self.contrada:
                if self.movement_hands[contrada]:
                    movement_card = random.choice(self.movement_hands[contrada])
                    self.positions[contrada] += int(movement_card)
                    self.movement_cards[contrada] = movement_card
                    self.movement_hands[contrada].remove(movement_card)
                    RaceScreen.discard_pile_movement.append(movement_card)
                    if RaceScreen.deck_movement:
                        self.movement_hands[contrada].append(RaceScreen.deck_movement.pop())

                if not self.special_disabled[contrada] and self.special_hands[contrada]:
                    special_card = random.choice(self.special_hands[contrada])
                    self.used_cards[contrada] = special_card.replace('_', ' ').capitalize()
                    if 'nerbata' in special_card and self.positions[contrada] > 0:
                        points = int(special_card.split('_')[1])
                        self.positions[contrada] -= abs(points)
                    elif 'sprona' in special_card:
                        points = int(special_card.split('_')[1])
                        self.positions[contrada] += points
                    elif 'sgambetto' in special_card:
                        for other_contrada, pos in sorted(self.positions.items(), key=lambda item: item[1], reverse=True):
                            if other_contrada != contrada and pos > self.positions[contrada]:
                                self.special_disabled[other_contrada] = True
                                break
                    self.special_hands[contrada].remove(special_card)
                    RaceScreen.discard_pile_special.append(special_card)
                    if RaceScreen.deck_special:
                        self.special_hands[contrada].append(RaceScreen.deck_special.pop())

    def draw_new_cards(self):
        for i in range(len(self.hand_movement)):
            if self.hand_movement[i] is None and RaceScreen.deck_movement:
                self.hand_movement[i] = RaceScreen.deck_movement.pop()
        for i in range(len(self.hand_special)):
            if self.hand_special[i] is None and RaceScreen.deck_special:
                self.hand_special[i] = RaceScreen.deck_special.pop()

        for contrada in self.positions:
            for i in range(len(self.movement_hands[contrada])):
                if self.movement_hands[contrada][i] is None and RaceScreen.deck_movement:
                    self.movement_hands[contrada][i] = RaceScreen.deck_movement.pop()
            for i in range(len(self.special_hands[contrada])):
                if self.special_hands[contrada][i] is None and RaceScreen.deck_special:
                    self.special_hands[contrada][i] = RaceScreen.deck_special.pop()

        self.update_card_buttons()

    def update_card_buttons(self):
        for i, card in enumerate(self.hand_movement):
            if card:
                self.card_buttons_movement[i].text = card
            else:
                self.card_buttons_movement[i].text = 'N/A'

        for i, card in enumerate(self.hand_special):
            if card:
                self.card_buttons_special[i].text = card.replace('_', ' ').capitalize()
                self.set_button_color(self.card_buttons_special[i], card)
                self.card_buttons_special[i].disabled = False if not self.special_disabled[self.contrada] else True
            else:
                self.card_buttons_special[i].text = 'N/A'
                self.card_buttons_special[i].background_color = (1, 1, 1, 0.8)

    def end_race(self):
        sorted_positions = sorted(self.positions.items(), key=lambda item: item[1], reverse=True)
        winner_position = sorted_positions[0][0]
        if self.positions[self.contrada] == self.positions[winner_position]:
            result_text = 'Hai vinto la gara!'
        else:
            result_text = f'Hai perso la gara. Ha vinto {winner_position}'
        
        result_text += '\n\nClassifica finale:\n'
        for pos, (contrada, score) in enumerate(sorted_positions, 1):
            result_text += f'{pos}. {contrada} (Cavallo: {self.horses[contrada]}): {score}\n'
        
        popup = Popup(title='Risultato Gara', content=Label(text=result_text), size_hint=(0.6, 0.6))
        popup.open()

class MyGameApp(App):
    def build(self):
        root = AnchorLayout()
        bg_image = Image(source='sfondo.jpg', allow_stretch=True, keep_ratio=False)
        root.add_widget(bg_image)
        game = MyGame()
        root.add_widget(game)
        return root

if __name__ == '__main__':
    MyGameApp().run()
