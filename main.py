import chess
import chess.engine

import threading

import pyttsx3 as tts
import speech_recognition as sr

from thefuzz import process

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import mainthread


transparent_png_dir = r"data\images\other\transparency.png"

image_dir = r"data\images\chess-pieces"

chess_engine_dir = r"data\engine\stockfish_15_win_x64_avx2\stockfish_15_x64_avx2.exe"

pieces_dict = {'p': image_dir + '\BlackPawn.png',
               'r': image_dir + '\BlackRook.png',
               'n': image_dir + '\BlackKnight.png',
               'b': image_dir + '\BlackBishop.png',
               'q': image_dir + '\BlackQueen.png',
               'k': image_dir + '\BlackKing.png',
               'P': image_dir + '\WhitePawn.png',
               'R': image_dir + '\WhiteRook.png',
               'N': image_dir + '\WhiteKnight.png',
               'B': image_dir + '\WhiteBishop.png',
               'Q': image_dir + '\WhiteQueen.png',
               'K': image_dir + '\WhiteKing.png',
               }

initial_pos_dict = {'a1': 'R',                    'a2': 'P',                    'a8': 'r',                    'a7': 'p',
                    'b1': 'N',                    'b2': 'P',                    'b8': 'n',                    'b7': 'p',
                    'c1': 'B',                    'c2': 'P',                    'c8': 'b',                    'c7': 'p',
                    'd1': 'Q',                    'd2': 'P',                    'd8': 'q',                    'd7': 'p',
                    'e1': 'K',                    'e2': 'P',                    'e8': 'k',                    'e7': 'p',
                    'f1': 'B',                    'f2': 'P',                    'f8': 'b',                    'f7': 'p',
                    'g1': 'N',                    'g2': 'P',                    'g8': 'n',                    'g7': 'p',
                    'h1': 'R',                    'h2': 'P',                    'h8': 'r',                    'h7': 'p',
                    }

square_names = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8',
                'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8',
                'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8',
                'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8']

piece_names_dict = {'pionek': chess.PAWN, 'pionka': chess.PAWN, 'pionkiem': chess.PAWN, 'pion': chess.PAWN,
                    'pionem': chess.PAWN, 'wie??a': chess.ROOK, 'wie????': chess.ROOK, 'wie????': chess.ROOK,
                    'skoczek': chess.KNIGHT, 'skoczka': chess.KNIGHT, 'skoczkiem': chess.KNIGHT, 'ko??': chess.KNIGHT,
                    'konia': chess.KNIGHT, 'koniem': chess.KNIGHT, 'konik': chess.KNIGHT, 'konikiem': chess.KNIGHT,
                    'goniec': chess.BISHOP, 'go??ca': chess.BISHOP, 'go??cem': chess.BISHOP, 'laufer': chess.BISHOP,
                    'laufera': chess.BISHOP, 'lauferem': chess.BISHOP, 'biskup': chess.BISHOP, 'biskupa': chess.BISHOP,
                    'biskupem': chess.BISHOP, 'kr??lowa': chess.QUEEN, 'kr??low??': chess.QUEEN, 'kr??l??wka': chess.QUEEN,
                    'kr??l??wk??': chess.QUEEN, 'hetman': chess.QUEEN, 'hetmana': chess.QUEEN, 'hetmanem': chess.QUEEN,
                    'kr??l': chess.KING, 'kr??la': chess.KING, 'kr??lem': chess.KING}

TTS = tts.init()
TTS.setProperty('volume', 0.7)
TTS.setProperty('rate', 190)
TTS.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PL-PL_PAULINA_11.0')

STT = sr.Recognizer()


class MyButton(ButtonBehavior, Image):  # W??asna klasa s??u????ca jako po????czenie obiekt??w image oraz button w kivy
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True
        self.highlight_rect = None
        self.highlight_ell = None
        self.highlight_lin = None


def get_color(num, highlight=False, clicked=False):  # Funkcja zwracaj??ca odpowiedni kolor do przekolorowania
    if clicked:
        if num % 2 != 0:
            return [112 / 255, 153 / 255, 194 / 255, 1]
        else:
            return [42 / 255, 83 / 255, 124 / 255, 1]
    elif highlight:
        if num % 2 != 0:
            return [205 / 255, 205 / 255, 205 / 255, 1]
        else:
            return [98 / 255, 98 / 255, 98 / 255, 1]
    else:
        if num % 2 != 0:
            return [1, 1, 1, 1]
        else:
            return [128 / 255, 128 / 255, 128 / 255, 1]


def update_rect_pieces(instance, *args):  # Jedna z funkcji aktualizuj??ca canvas aby pozwoli?? na przesuwanie ekranu
    instance.rect.pos = instance.pos
    instance.rect.size = instance.size


def update_rect(instance, *args):  # Jedna z funkcji aktualizuj??ca canvas aby pozwoli?? na przesuwanie ekranu
    if instance.highlight_rect:
        instance.highlight_rect.pos = instance.pos
        instance.highlight_rect.size = instance.size
    instance.rect.pos = instance.pos
    instance.rect.size = instance.size


def update_ellipse(instance, *args):  # Jedna z funkcji aktualizuj??ca canvas aby pozwoli?? na przesuwanie ekranu
    if instance.highlight_ell:
        instance.highlight_ell.pos = [instance.center_x - instance.size[0] / 6,
                                      instance.center_y - instance.size[1] / 6]
        instance.highlight_ell.size = [instance.size[0] / 3, instance.size[1] / 3]


def update_line(instance, *args):  # Jedna z funkcji aktualizuj??ca canvas aby pozwoli?? na przesuwanie ekranu
    if instance.highlight_lin:
        instance.highlight_lin.width = 3 * (Window.size[1] / 800)
        instance.highlight_lin.circle = (
            instance.center_x, instance.center_y, min(instance.width, instance.height) / 2.5)


class WelcomeScreen(Screen):  # Klasa odpowiadaj??ca za ekran tytu??owy implementuje si?? ona z pliku main.kv
    def game_mode_change(self, mode):
        if mode:
            self.manager.get_screen('chess_board').multiplayer = True
        else:
            self.manager.get_screen('chess_board').multiplayer = False
            self.manager.get_screen('chess_board').start_engine()


def get_coords(board_coords):  # Funkcja zmieniaj??ca koordynaty symulacji na koordynaty w gui
    return board_coords + (7 - (board_coords % 8) * 2)


class ChessBoard(Screen):  # G????wna klasa zajmuj??ca si?? ca??o??ci?? graficzn?? gry
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = None
        self.board_sim = chess.Board()
        self.legal_moves = list(self.board_sim.legal_moves)
        self.colored_pieces = []
        self.last_piece_pressed = None
        self.possible_moves = []
        self.promotion = False
        self.promotion_type = ''
        self.curr_instance = None
        self.checked_king = None
        self.multiplayer = False
        self.engine = None
        self.white_beaten = 0
        self.black_beaten = 0
        self.proposed_move = None
        self.wait_flag = False
        self.request_close = False
        self.request_close_wait = False
        self.event_obj = None

        # Utworzenie osobnego w??tku odpowiedzialnego za nas??uchiwanie
        self.voice_thread = threading.Thread(target=self.voice_recognition_func, args=())
        self.voice_thread.start()

        # Ustalanie wielko??ci okna w formacie 16:9 oraz funkcji odpowiedzialnej za poprawne zamkni??cie proces??w
        Window.size = [1280, 720]
        Window.bind(on_request_close=self.on_request_close)

        # Utworzenie graficznej reprezentacji planszy
        self.board = GridLayout(cols=8, spacing=0, size_hint=(.9, 1))
        for i in range(8):
            for j in range(8):
                coords = chr(97 + j) + str(8 - i)
                if i in [0, 1, 6, 7]:
                    piece = initial_pos_dict[coords]
                    image = pieces_dict[piece]
                else:
                    piece = None
                    image = transparent_png_dir

                btn = MyButton(source=image)

                btn.coords = coords
                btn.piece = piece
                with btn.canvas.before:
                    curr_color = get_color(i + j + 1)
                    Color(curr_color[0], curr_color[1], curr_color[2], 1)
                    btn.rect = Rectangle(size=btn.size, pos=btn.pos)

                btn.bind(pos=update_rect, size=update_rect)
                btn.bind(pos=update_line, size=update_line)
                btn.bind(pos=update_ellipse, size=update_ellipse)
                btn.bind(on_press=self.on_press_func)
                self.board.add_widget(btn)

        # Utworzenie "obwoluty" dooko??a planszy opisuj??cej pozycj??
        nums1 = BoxLayout(orientation='vertical', size_hint=(.05, 1))
        nums1.add_widget(Label(text='8'))
        nums1.add_widget(Label(text='7'))
        nums1.add_widget(Label(text='6'))
        nums1.add_widget(Label(text='5'))
        nums1.add_widget(Label(text='4'))
        nums1.add_widget(Label(text='3'))
        nums1.add_widget(Label(text='2'))
        nums1.add_widget(Label(text='1'))

        nums2 = BoxLayout(orientation='vertical', size_hint=(.05, 1))
        nums2.add_widget(Label(text='8'))
        nums2.add_widget(Label(text='7'))
        nums2.add_widget(Label(text='6'))
        nums2.add_widget(Label(text='5'))
        nums2.add_widget(Label(text='4'))
        nums2.add_widget(Label(text='3'))
        nums2.add_widget(Label(text='2'))
        nums2.add_widget(Label(text='1'))

        chars1 = BoxLayout(orientation='horizontal', size_hint=(1, .05))
        chars1.add_widget(Label(text='a'))
        chars1.add_widget(Label(text='b'))
        chars1.add_widget(Label(text='c'))
        chars1.add_widget(Label(text='d'))
        chars1.add_widget(Label(text='e'))
        chars1.add_widget(Label(text='f'))
        chars1.add_widget(Label(text='g'))
        chars1.add_widget(Label(text='h'))

        chars2 = BoxLayout(orientation='horizontal', size_hint=(1, .05))
        chars2.add_widget(Label(text='a'))
        chars2.add_widget(Label(text='b'))
        chars2.add_widget(Label(text='c'))
        chars2.add_widget(Label(text='d'))
        chars2.add_widget(Label(text='e'))
        chars2.add_widget(Label(text='f'))
        chars2.add_widget(Label(text='g'))
        chars2.add_widget(Label(text='h'))

        board_nums_chars = GridLayout(cols=3, spacing=0, size_hint=(1, .95))

        board_nums_chars.add_widget(Label(text='', size_hint=(.05, .05)))
        board_nums_chars.add_widget(chars1)
        board_nums_chars.add_widget(Label(text='', size_hint=(.05, .05)))
        board_nums_chars.add_widget(nums2)
        board_nums_chars.add_widget(self.board)
        board_nums_chars.add_widget(nums1)
        board_nums_chars.add_widget(Label(text='', size_hint=(.05, .05)))
        board_nums_chars.add_widget(chars2)
        board_nums_chars.add_widget(Label(text='', size_hint=(.05, .05)))

        board_nums_chars_input_space = BoxLayout(orientation='vertical', size_hint=(.54, 1))

        text_input = TextInput(text='', multiline=False, size_hint=(1, .05))
        text_input.bind(on_text_validate=self.text_input)

        board_nums_chars_input_space.add_widget(board_nums_chars)
        board_nums_chars_input_space.add_widget(text_input)

        # Utworzenie obszaru, w kt??rym wy??wietlane b??d?? zbite figury
        self.infobox_left = BoxLayout(orientation='vertical', size_hint=(.23, 1))

        beaten_figures_white = GridLayout(cols=4, spacing=0, size_hint=(1, .25))
        beaten_figures_black = GridLayout(cols=4, spacing=0, size_hint=(1, .25))

        for i in range(16):
            beaten_figures_white.add_widget(Image(source=transparent_png_dir))
            beaten_figures_black.add_widget(Image(source=transparent_png_dir))

        empty_space = Image(source=transparent_png_dir, size_hint=(1, .5))

        with self.infobox_left.canvas.before:
            Color(128 / 255, 128 / 255, 128 / 255, 1)
            self.infobox_left.rect = Rectangle(size=self.infobox_left.size, pos=self.infobox_left.pos)

        self.infobox_left.bind(pos=update_rect_pieces, size=update_rect_pieces)

        self.infobox_left.add_widget(beaten_figures_white)
        self.infobox_left.add_widget(empty_space)
        self.infobox_left.add_widget(beaten_figures_black)

        infobox_right = BoxLayout(orientation='vertical', size_hint=(.23, 1))

        self.tmp_speech_button = Button(text='Naci??nij i m??w')
        self.tmp_speech_button.bind(on_press=self.tmp_voice_thread_release)

        infobox_right.add_widget(self.tmp_speech_button)

        parent_widget = BoxLayout(orientation='horizontal')

        parent_widget.add_widget(self.infobox_left)
        parent_widget.add_widget(board_nums_chars_input_space)
        parent_widget.add_widget(infobox_right)

        self.add_widget(parent_widget)

        # Utworzenie wiadomo??ci typu popup pytaj??cych o promocj?? figury informuj??cych o zako??czeniu gry b??d?? o braku
        # podpi??tego mikrofonu
        choice_boxes = BoxLayout(orientation='horizontal')
        btn1_white = MyButton(source=pieces_dict['Q'])
        btn1_white.piece = 'q'
        btn1_white.bind(on_press=self.promotion_change)
        choice_boxes.add_widget(btn1_white)
        btn2_white = MyButton(source=pieces_dict['B'])
        btn2_white.piece = 'b'
        btn2_white.bind(on_press=self.promotion_change)
        choice_boxes.add_widget(btn2_white)
        btn3_white = MyButton(source=pieces_dict['N'])
        btn3_white.piece = 'n'
        btn3_white.bind(on_press=self.promotion_change)
        choice_boxes.add_widget(btn3_white)
        btn4_white = MyButton(source=pieces_dict['R'])
        btn4_white.piece = 'r'
        btn4_white.bind(on_press=self.promotion_change)
        choice_boxes.add_widget(btn4_white)
        self.popup_white_promotion = Popup(title='Wybierz promocj??', size_hint=(None, None), size=(300, 200),
                                           background_color=(1, 1, 1, 1), auto_dismiss=False,
                                           content=choice_boxes)

        choice_boxes_black = BoxLayout(orientation='horizontal')
        btn1_black = MyButton(source=pieces_dict['q'])
        btn1_black.piece = 'q'
        btn1_black.bind(on_press=self.promotion_change)
        choice_boxes_black.add_widget(btn1_black)
        btn2_black = MyButton(source=pieces_dict['b'])
        btn2_black.piece = 'b'
        btn2_black.bind(on_press=self.promotion_change)
        choice_boxes_black.add_widget(btn2_black)
        btn3_black = MyButton(source=pieces_dict['n'])
        btn3_black.piece = 'n'
        btn3_black.bind(on_press=self.promotion_change)
        choice_boxes_black.add_widget(btn3_black)
        btn4_black = MyButton(source=pieces_dict['r'])
        btn4_black.piece = 'r'
        btn4_black.bind(on_press=self.promotion_change)
        choice_boxes_black.add_widget(btn4_black)
        self.popup_black_promotion = Popup(title='Wybierz promocj??', size_hint=(None, None), size=(300, 200),
                                           background_color=(1, 1, 1, 1), auto_dismiss=False,
                                           content=choice_boxes_black)

        choice_boxes_game_end = BoxLayout(orientation='horizontal')
        btn1 = Button(text='Main Menu', background_normal='', background_color=(0.47, 0.3, 0.2, 1))
        btn1.bind(on_press=self.game_end)
        choice_boxes_game_end.add_widget(btn1)
        btn2 = Button(text='Restart', background_normal='', background_color=(0.47, 0.3, 0.2, 1))
        btn2.bind(on_press=self.game_end)
        choice_boxes_game_end.add_widget(btn2)
        self.popup_game_end = Popup(title='Depends', size_hint=(None, None), size=(300, 150),
                                    background_color=(1, 1, 1, 1), content=choice_boxes_game_end)

        self.no_microphone_error_popup = Popup(title='Nie wykryto mikrofonu', size_hint=(None, None), size=(300, 150),
                                               background_color=(1, 1, 1, 1))

    def tmp_voice_thread_release(self, instance):  # Funkcja odpowiedzialna za "puszczenie" w??tku nas??uchuj??cego
        instance.disabled = True
        self.event_obj.set()

    @mainthread  # Dekorator s??u????cy wywo??aniu danej funkcji w g????wnym w??tku gdy?? tak nale??y operowa?? w przypadku gui
    def no_microphone_error_popup_func(self):  # Funkcja odpowiedzialna za wy??wietlenie informacji o braku mikrofonu
        self.no_microphone_error_popup.open()

    def voice_recognition_func(self):  # Funkcja odpowiedzialna za rozpoznanie g??osu
        while True:
            # Tworzy zdarzenie nast??pnie sama si?? nim blokuje czekaj??c na naci??ni??cie guzika przez u??ytkownika
            self.event_obj = threading.Event()
            self.event_obj.wait()
            # B??d?? na zamkni??cie programu
            if self.request_close:
                break
            try:  # Pr??ba nas??uchiwania zwr??ci exception, je??li nie ma podpi??tego mikrofonu
                self.request_close_wait = True
                with sr.Microphone() as source:
                    try:
                        # Nas??uchiwanie u??ytkownika przez 3 sek, nast??pnie timeout aby unikn???? niesko??czonego czekania
                        audio = STT.listen(source, timeout=3, phrase_time_limit=3)
                        text = STT.recognize_google(audio, language='pl_PL')
                        text.replace(' ', '')

                        # Interpretacja uzyskanego tekstu
                        from_square = process.extract(text[0:2], square_names)
                        piece_name = process.extract(text, list(piece_names_dict.keys()))
                        to_square = process.extract(text[2:], square_names)
                        promotion = process.extract(text[4:], list(piece_names_dict.keys()))
                        if promotion[0][1] < 100:
                            promotion = ''
                        else:
                            promotion = promotion[0][0]

                        if (from_square[0][1] < 90 and piece_name[0][1] < 90) or to_square[0][1] < 90 \
                                or from_square[0][0] == to_square[0][0]:
                            pass
                            # TTS.say('Nie rozumiem')
                            # TTS.runAndWait()
                        else:
                            if piece_name[0][1] >= 90 and to_square[0][1] >= 90:
                                possible_pieces = list(
                                    self.board_sim.pieces(piece_names_dict[piece_name[0][0]], self.board_sim.turn))

                                # Je??li komenda zaczyna si?? od nazwy figury, znalezienie wszystkich mo??liwych jej ruch??w
                                matching = []

                                for square_with_piece in possible_pieces:
                                    tmp = [str(s)[:2] for s in self.legal_moves if
                                           chess.square_name(square_with_piece) in str(s)[:2]
                                           and to_square[0][0] in str(s)[2:4]]
                                    if tmp:
                                        matching.append(tmp[0])

                                # Je??li wi??cej ni?? jedna taka sama figura mo??e dokona?? danego ruchu program prosi o
                                # sprecyzowanie lokalizacji startowej
                                if len(matching) > 1:
                                    TTS.say('Sprecyzuj lokalizacj?? figury')
                                    TTS.runAndWait()
                                    audio = STT.listen(source, timeout=3, phrase_time_limit=3)
                                    text = STT.recognize_google(audio, language='pl_PL')
                                    from_square = process.extract(text, square_names)
                                    if from_square[0][1] < 90 or from_square[0][0] == to_square[0][0]:
                                        break
                                        # TTS.say('Nie rozumiem, spr??buj ponownie2')
                                        # TTS.runAndWait()
                                elif len(matching) == 1:
                                    from_square = [[matching[0][:2]]]  # just don't question it

                            # Utworzenie proponowanego ruchu
                            self.proposed_move = chess.Move.from_uci(from_square[0][0] + to_square[0][0] + promotion)

                            # Je??li znajduje si?? na li??cie wszystkich mo??liwych, jest wykonany, je??li nie ale nie
                            # zarejestrowano informacji o promocji, sprawdzenie, czy da si?? wykona?? # taki ruch,
                            # je??li tak program prosi o wyb??r promocji przez u??ytkownika
                            if self.proposed_move in self.legal_moves:
                                self.chess_move(False, self.proposed_move)
                            elif promotion == '' and chess.Move.from_uci(
                                    from_square[0][0] + to_square[0][0] + 'q') in self.legal_moves:
                                TTS.say('Wybierz promocj??')
                                TTS.runAndWait()
                                audio = STT.listen(source, timeout=3, phrase_time_limit=3)
                                text = STT.recognize_google(audio, language='pl_PL')
                                promotion = process.extract(text, list(piece_names_dict.keys()))
                                if promotion[0][1] >= 90:
                                    self.promotion_type = chess.piece_symbol(piece_names_dict[promotion[0][0]])
                                    self.chess_move(False, self.proposed_move)
                    except sr.UnknownValueError:
                        TTS.say('Nie rozumiem')
                        TTS.runAndWait()
                    except sr.RequestError as e:
                        pass
                        # print('error:', e)
            except OSError:  # ??apanie exception zwi??zane z brakiem mikrofonu i informowanie u??ytkownika
                self.no_microphone_error_popup_func()

            self.request_close_wait = False
            self.tmp_speech_button.disabled = False

    def text_input(self, instance):  # Funkcja zajmuj??ca si?? r??cznie wpisanym ruchem przez u??ytkownika
        txt = instance.text
        instance.text = ''
        if txt == '':
            pass
        from_square = process.extract(txt[0:2], square_names)
        to_square = process.extract(txt[2:], square_names)

        if from_square[0][1] < 90 or to_square[0][1] < 90 or from_square[0][0] == to_square[0][0]:
            pass
        else:
            self.proposed_move = chess.Move.from_uci(from_square[0][0] + to_square[0][0])

            if self.proposed_move in self.legal_moves:
                self.chess_move(False, self.proposed_move)
            elif chess.Move.from_uci(from_square[0][0] + to_square[0][0] + 'q') in self.legal_moves:
                if self.board_sim.turn:
                    self.popup_white_promotion.open()
                else:
                    self.popup_black_promotion.open()

    def on_request_close(self, *args, **kwargs):  # Funkcja zapewniaj??ca poprawne zamkni??cie programu
        if self.request_close_wait:
            return True
        self.request_close = True
        self.event_obj.set()
        if self.engine:
            self.end_engine()
        self.voice_thread.join()

    def start_engine(self):  # Funkcja odpowiedzialna za start silnika w trybie jednoosobowym
        self.engine = chess.engine.SimpleEngine.popen_uci(chess_engine_dir)

    def end_engine(self):  # Funkcja odpowiedzialna za wy????czenie silnika w trybie jednoosobowym
        self.engine.quit()

    def board_rebuild(self):  # Funkcja odbudowuj??ca plansz?? po resecie
        for child in self.board.children:
            if child.coords[1] in ['1', '2', '7', '8']:
                piece = initial_pos_dict[child.coords]
                image = pieces_dict[piece]
            else:
                piece = None
                image = transparent_png_dir

            child.source = image
            child.piece = piece

            with child.canvas.before:
                curr_color = get_color(ord(child.coords[1]) + ord(child.coords[0]))
                Color(curr_color[0], curr_color[1], curr_color[2], 1)
                child.rect = Rectangle(size=child.size, pos=child.pos)

        for child in self.infobox_left.children[0].children:
            child.source = transparent_png_dir

        for child in self.infobox_left.children[2].children:
            child.source = transparent_png_dir

        self.white_beaten = 0
        self.black_beaten = 0

    def game_reset(self):  # Funkcja odpowiedzialna za reset gry
        self.board_sim.reset()
        self.board_rebuild()
        self.board_sim.turn = chess.WHITE
        self.legal_moves = list(self.board_sim.legal_moves)

    def game_end(self, instance):  # Funkcja odpowiedzialna za zako??czenie gry i mo??liwy powr??t do ekranu tytu??owego
        if instance.text == 'Main Menu':
            self.manager.transition.direction = "left"
            self.manager.current = 'welcome'
        self.game_reset()
        self.popup_game_end.dismiss()

    def promotion_change(self, instance):  # Funkcja wywo??ywana poprzez wybranie promocji podczas sterowania r??cznego
        self.promotion_type = instance.piece
        self.popup_white_promotion.dismiss()
        self.popup_black_promotion.dismiss()
        self.chess_move(False, self.proposed_move)

    def highlight_recolor(self, matching, mode=False, clicked=False):  # Funkcja zajmuj??ca si?? przekolorowywaniem ekranu
        for position in matching:
            if len(str(position)) == 5:
                self.promotion = True
            if isinstance(position, str):
                pos_val = (ord(position[-2]) - 97 + (ord(position[-1]) - 49) * 8)
            else:
                pos_val = position.to_square

            if mode and not clicked:
                self.colored_pieces.append(position)
                self.possible_moves.append(str(position)[2:4])

            btn = self.board.children[get_coords(pos_val)]

            if not mode:
                while len(btn.canvas.before.children) > 3:
                    btn.canvas.before.children.pop()
                if btn.piece in ['k', 'K'] and self.board_sim.is_check():
                    with btn.canvas.before:
                        Color(1, 0, 0, 1)
                        btn.highlight_rect = Rectangle(size=btn.size, pos=btn.pos)
            else:
                with btn.canvas.before:
                    if clicked:
                        curr_color = get_color(pos_val + pos_val // 8, True, True)
                    else:
                        curr_color = get_color(pos_val + pos_val // 8, True)

                    Color(curr_color[0], curr_color[1], curr_color[2], 1)

                    if clicked:
                        btn.highlight_rect = Rectangle(size=btn.size, pos=btn.pos)
                    elif btn.piece:
                        btn.highlight_lin = Line(width=3,
                                                 circle=(btn.center_x, btn.center_y, min(btn.width, btn.height) / 2.5))
                    else:
                        btn.highlight_ell = Ellipse(size=[btn.size[0] / 3, btn.size[1] / 3],
                                                    pos=[btn.center_x - btn.size[0] / 6,
                                                         btn.center_y - btn.size[1] / 6])

    def king_check_highlight(self, end=False):  # Osobna funkcja dla kr??la, gdy ma miejsce szach
        king_pos = self.board_sim.king(self.board_sim.turn)
        btn = self.board.children[get_coords(king_pos)]
        with btn.canvas.before:
            if end:
                curr_color = get_color(king_pos + king_pos // 8)
                Color(curr_color[0], curr_color[1], curr_color[2], 1)
            else:
                Color(1, 0, 0, 1)
            btn.highlight = Rectangle(size=btn.size, pos=btn.pos)
        btn.bind(pos=update_rect, size=update_rect)

    @mainthread  # Dekorator s??u????cy wywo??aniu danej funkcji w g????wnym w??tku, gdy?? tak nale??y operowa?? w przypadku gui
    def chess_move(self, bot=False, move=None):  # Funkcja wykonuj??ca ruch niezale??nie od metody sterowania
        if self.colored_pieces:
            self.highlight_recolor(self.colored_pieces, False)
            self.colored_pieces = []
        if self.last_piece_pressed:
            self.highlight_recolor([self.last_piece_pressed.coords], False, True)
        if move:
            if self.promotion_type:
                move = chess.Move.from_uci(
                    chess.square_name(move.from_square) + chess.square_name(move.to_square) + self.promotion_type)
            self.last_piece_pressed = self.board.children[get_coords(move.from_square)]
            self.curr_instance = self.board.children[get_coords(move.to_square)]
        elif bot:
            move = self.engine.play(self.board_sim, chess.engine.Limit(time=0.1)).move
            self.last_piece_pressed = self.board.children[get_coords(move.from_square)]
            self.curr_instance = self.board.children[get_coords(move.to_square)]
            if len(str(move)) == 5:
                self.promotion_type = str(move)[4]
        else:
            move = chess.Move.from_uci(
                str(self.last_piece_pressed.coords) + str(self.curr_instance.coords) + self.promotion_type)

        if self.board_sim.has_legal_en_passant() and self.board_sim.is_en_passant(move):
            self.board.children[get_coords(
                self.board_sim.ep_square + (8 * (-1 if self.board_sim.turn else 1)))].source = transparent_png_dir

        if self.promotion_type:
            self.last_piece_pressed.source = pieces_dict[
                self.promotion_type.upper() if self.board_sim.turn else self.promotion_type]
        if self.curr_instance.piece:
            if self.board_sim.turn:
                self.infobox_left.children[0].children[self.white_beaten].source = self.curr_instance.source
                self.white_beaten += 1
            else:
                self.infobox_left.children[2].children[
                    self.black_beaten + (4 * (3 - (self.black_beaten // 4) * 2))].source = self.curr_instance.source
                self.black_beaten += 1

        self.curr_instance.source = self.last_piece_pressed.source
        self.last_piece_pressed.source = transparent_png_dir

        if self.board_sim.is_check():
            self.king_check_highlight(True)

        if self.board_sim.is_castling(move):
            if self.board_sim.is_queenside_castling(move):
                self.board.children[7 if self.board_sim.turn else 63].source = transparent_png_dir
                self.board.children[4 if self.board_sim.turn else 60].source = pieces_dict[
                    'R' if self.board_sim.turn else 'r']
            else:
                self.board.children[0 if self.board_sim.turn else 56].source = transparent_png_dir
                self.board.children[2 if self.board_sim.turn else 58].source = pieces_dict[
                    'R' if self.board_sim.turn else 'r']

        self.board_sim.push(move)

        self.curr_instance.piece = self.last_piece_pressed.piece
        self.last_piece_pressed.piece = None
        self.promotion = False
        self.last_piece_pressed = None
        self.proposed_move = None
        self.promotion_type = ''

        if self.board_sim.outcome():
            if self.board_sim.outcome().winner:
                self.popup_game_end.title = "Bia??y gracz wygra??"
            else:
                self.popup_game_end.title = "Czarny gracz wygra??"
            self.popup_game_end.open()
        else:
            self.legal_moves = list(self.board_sim.legal_moves)
            if self.board_sim.is_check():
                self.king_check_highlight()
            # Je??li w????czony jest tryb jednoosobowy, funkcja wywo??uje si?? sama uzyskuj??c ruch od silnika szachowego
            if not self.multiplayer and not bot:
                self.chess_move(True)

    def on_press_func(self, instance):  # Funkcja zajmuj??ca si?? trybem sterowania poprzez klikanie figur na planszy
        if instance.coords in self.possible_moves:
            self.highlight_recolor(self.colored_pieces)
            self.highlight_recolor([self.last_piece_pressed.coords], False, True)
            self.colored_pieces = []
            self.possible_moves = []
            self.curr_instance = instance

            if self.promotion:
                if self.board_sim.turn:
                    self.popup_white_promotion.open()
                else:
                    self.popup_black_promotion.open()
            else:
                self.promotion_type = ''
                self.chess_move()
        else:
            matching = [s for s in self.legal_moves if instance.coords in str(s)[:2]]
            self.promotion = False
            if not matching:
                self.highlight_recolor(self.colored_pieces, False)
                self.highlight_recolor([instance.coords], False, True)
                if self.last_piece_pressed:
                    self.highlight_recolor([self.last_piece_pressed.coords], False, True)
                self.colored_pieces = []
                self.possible_moves = []
                self.last_piece_pressed = None
            else:
                if not self.last_piece_pressed:
                    self.highlight_recolor(matching, True)
                    self.highlight_recolor([instance.coords], True, True)
                    self.last_piece_pressed = instance
                elif self.last_piece_pressed == instance:
                    self.possible_moves = []
                    self.highlight_recolor(matching, False)
                    self.highlight_recolor([instance.coords], True, True)
                    self.highlight_recolor([instance.coords], False, True)
                    self.last_piece_pressed = None
                else:
                    self.highlight_recolor(self.colored_pieces, False)
                    self.highlight_recolor([self.last_piece_pressed.coords], False, True)
                    self.colored_pieces = []
                    self.possible_moves = []
                    self.highlight_recolor(matching, True)
                    self.highlight_recolor([instance.coords], True, True)
                    self.last_piece_pressed = instance


class WindowManager(ScreenManager):  # Manager wielu okien, implementowany z pliku main.kv
    pass


class ChessApp(App):  # G????wna aplikacja, implementowana z pliku main.kv, s??u??y jako nadrz??dny obiekt dla pozosta??ych ekran??w
    def build(self):
        return Builder.load_file('main.kv')


if __name__ == "__main__":
    ChessApp().run()
