# Mensch Ärgere Dich Nicht!
# created on 17.11.2020 by JPW

import random
import time
import colorama
colorama.init()

# Was funktioniert:
# - Spielfeld Loop
# - Beliebige Spieleranzahl
# - (simple) Spielfeldanzeige
# - Rausschmeissen
# - 3 Versuche, wenn keine Figur auf dem Feld ist

# Einschränkungen:
# - Zielsortierung ist egal
# - Wenn man freimachen muss, kann es zu zwei Figuren auf einem Feld kommen (siehe TODO)

class MenschAergereDichNicht:
    # Class attribute
    version = "1.0"

    # Game
    def __init__(self, number_of_players):
        # instance attribute
        self.number_of_players = number_of_players
        self.game_size = number_of_players * 10
        self.players = []
        self.game_over = False
        
        print("starting...", self.number_of_players, "Players")

        # init gamefield display
        self.gamefield = Gamefield(self)

        for p in range(self.number_of_players):
            self.players.append(Player(self, p*10, p))

        # Main Game Loop
        while True:
            for player in self.players:
                # show gamefield before every turn
                self.gamefield.show(self.players)

                print("")
                print("Players", player.id+1, "Turn")

                player.turn()

                if player.has_won():
                    print("Game Over")
                    print("Player", player.id+1, "has won")
                    return


class Player:
    def __init__(self, parent, offset, id):
        self.parent = parent
        self.offset = offset
        self.name = "Player " + str(id)
        self.pieces = []
        self.id = id

        # Every player owns 4 pieces
        for _ in range(0,4):
            self.pieces.append(Piece(self))

    # true if one (or more) pieces is on the board
    def has_piece_outside(self):
        result = False
        for piece in self.pieces:
            if piece.position != -1 and piece.position < self.parent.game_size:
                result = True
        return result
    
    # seperate function needed, true if one (or more) pieces is in start
    def has_piece_inside(self):
        result = False
        for piece in self.pieces:
            if piece.position == -1:
                result = True
        return result

    # returns REAL (gamefield) positions of all 4 pieces (with offset)
    def get_piece_positions_offset(self):
        positions = []
        for piece in self.pieces:
            # old:
            # positions.append(piece.get_realposition())
            positions.append(self.calculate_realposition(piece))
        return positions

    # move piece from start area to board
    def place_piece_outside(self):
        for piece in self.pieces:
            if piece.position == -1:
                # kick other players from the start point
                if self.is_field_free(self.offset):
                    piece.position = 0
                    return
        print("ERROR: player has no piece in start area")

    # Returns the piece object on starting point of current player
    def get_piece_on_start(self):
        for piece in self.pieces:
            if piece.position == 0:
                return piece
        return False

    # true if all pieces are in finish, expansion possible
    def has_won(self):
        won = True
        for piece in self.pieces:
            if piece.position < self.parent.game_size:
                won = False
        return won

    # main function, gets called every turn
    def turn(self):
        # Positions
        #print("Player", self.id+1, "Positions:", self.get_piece_positions())
        # Real Positions
        print("Player", self.id+1, "Positions:", self.get_piece_positions_offset())

        piece_on_start = self.get_piece_on_start()

        # is the player allowed to throw the dice 3 times?
        if self.has_piece_outside():
            # normal game
            dice = self.roll_dice()

            # Special Cases when a 6 is thrown:
            if dice == 6:
                # bonus roll
                next_dice = self.roll_dice()

                if self.has_piece_inside():
                    if not piece_on_start:
                        i = input("Move Piece from home to board? (y/n)")
                        if i != "n":
                            # the first dice (6) will get used to place the piece
                            self.place_piece_outside()
                            piece_on_start = self.get_piece_on_start()
                            if self.has_piece_inside():
                                # has to move from start
                                # TODO: check for kick and own pieces!
                                piece_on_start.go_forward(next_dice)
                            else:
                                self.move_freely(next_dice)
                        else:
                            # the first dice (6) can be used to walk
                            self.move_freely(dice)
                            self.move_freely(next_dice)
                    else:
                        # has to move from start, TODO check for kick and own pieces
                        piece_on_start.go_forward(next_dice)
                else:
                    # player cant use the dice to get out of start anyways
                    self.move_freely(dice)
                    self.move_freely(next_dice)

                if next_dice == 6:
                    # repeat if the next throw was another 6
                    self.turn()
            else:
                # normal gameplay
                self.move_freely(dice)
        else:
            # roll 3 times to get out of start
            for i in range(0, 3):
                print("Roll", i+1)
                dice = self.roll_dice()
                if dice == 6:
                    next_dice = self.roll_dice()
                    self.place_piece_outside()
                    # TODO: check for kick and own pieces!
                    self.get_piece_on_start().go_forward(next_dice)
                    if next_dice == 6:
                        self.turn()
                    break

    # player can (freely) select which piece to move (i.e. doesnt need to move from start)
    def move_freely(self, dice):
        i = int(input("Select Piece: "))
        pos_real = self.calculate_realposition(self.pieces[i-1])
        newpos_real = self.calculate_realposition(self.pieces[i-1], dice)

        if pos_real != "Start" and pos_real != "Finish" and newpos_real != "Outside" :
            if self.is_field_free(newpos_real):
                self.pieces[i-1].go_forward(dice)
            else:
                # Man kann sich nicht selber rausschlagen und muss eine andere Figur nehmen.
                # TODO: was ist wenn das nicht möglich ist..?
                pass
        else:
            print("Cant move this piece")
            self.move_freely(dice)

    # Returns number between 1 and 6
    def roll_dice(self):
        dice = random.randint(1, 6)
        print("Rolling dice:", dice)
        return dice

    # check if field is free and kick other players if needed
    def is_field_free(self, realposition):
        free = True

        for player in self.parent.players:
            if player.id != self.id: # check for other player pieces
                for piece in player.pieces:
                    if piece.position < self.parent.game_size and piece.position != -1 and self.calculate_realposition(piece) == realposition:
                        print("kicking piece on position", realposition, " owner: player", player.id+1)
                        piece.position = -1
            else: # check for own pieces
                for piece in player.pieces:
                    if self.calculate_realposition(piece) == realposition and self.calculate_realposition(piece) != "Finish": # and realposition is inside finish
                        print("Field is not free or outside the board")
                        free = False
        return free

    # returns the real positon of a piece. use dice to check future positions, leave blank to use default 0 (current position)
    def calculate_realposition(self, piece, dice=0):
        position = piece.position + dice
        boardsize = self.parent.game_size

        # Preparation for finish-sorting
        # Check for start/finish
        #if boardsize <= position <= boardsize+3:
        #    return "Finish"
        #if position > boardsize+3:
        #    return "Outside"

        # atm no check in finish
        if boardsize <= position:
            return "Finish"
        if position == -1:
            return "Start"


        # offset-calculation-wrap-around-magic - do not touch
        if piece.parent.offset != 0:
            if position >= (boardsize-piece.parent.offset):
                return position - (boardsize-piece.parent.offset)
            else:
                return position + piece.parent.offset
        else:
            return position

    # preparation for custom player names
    def set_name(self, name):
        self.name = name


class Piece:
    def __init__(self, parent):
        self.parent = parent
        self.position = -1

    # move piece, do not call directly, use player-functions as wrapper to handle kicking etc
    def go_forward(self, distance):
        print("Moving piece from", self.position, "to", self.position + distance)
        self.position = self.position + distance
        print("Real new position:", self.parent.calculate_realposition(self))


class Gamefield:
    def __init__(self, parent):
        self.parent = parent
        self.size = self.parent.game_size
        self.color = [colorama.Fore.RED, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.BLUE, colorama.Fore.MAGENTA, colorama.Fore.CYAN, colorama.Back.RED, colorama.Back.GREEN, colorama.Back.YELLOW, colorama.Back.BLUE, colorama.Back.MAGENTA, colorama.Back.CYAN, colorama.Back.WHITE]
        self.color_reset = colorama.Fore.RESET + colorama.Back.RESET
    
    # Output a simple board
    def show(self, players):
        # check for pieces in finish
        print ("Finish: ", end='')
        for player_index, player in enumerate(players):
            for piece_index, piece in enumerate(player.pieces):
                if "Finish" == player.calculate_realposition(piece):
                    print(self.color[player_index] + str(piece_index+1) + self.color_reset, end='')
        # newline
        print("")

        # show board from end to start (descending)
        for i in reversed(range(0, self.size)):
            # add space for single digits
            if i < 10:
                print(" ", end='')

            print (str(i) + ": ", end='')

            # show pieces in player colors
            for player_index, player in enumerate(players):
                for piece_index, piece in enumerate(player.pieces):
                    if i == player.calculate_realposition(piece):
                        print(self.color[player_index] + str(piece_index+1) + self.color_reset, end='')

            # show start/finish locations in player colors
            for player_index, player in enumerate(players):
                if i == player.offset:
                    print(self.color[player_index] + "  (Start/Finish Player " + str(player_index+1) + ")" + self.color_reset, end='')

            #newline
            print("")


if __name__ == "__main__":
    # Start the game
    game = MenschAergereDichNicht(3)
    print("Version", game.version)
