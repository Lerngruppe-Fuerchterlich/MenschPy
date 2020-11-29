# Mensch Ärgere Dich Nicht!
# created on 17.11.2020 by JPW

import random
import time
import colorama
colorama.init()

# TODO: Ziel abfrage überarbeiten
# TODO: class diagram


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

        self.gamefield = Gamefield(self)

        for p in range(self.number_of_players):
            self.players.append(Player(self, p*10, p))

        while True:
            for player in self.players:
                print("")
                print("Players", player.id+1, "Turn")

                self.gamefield.show(self.players)

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

        for x in range(0,4):
            self.pieces.append(Piece(self))

    # true if one (or more) pieces is on the board
    def has_piece_outside(self):
        result = False
        for piece in self.pieces:
            # TODO: add check if piece is in the finish and cant move (to grant the player 3 dice rolls)
            if piece.position != -1:
                result = True
        return result
    
    # seperate function needed, true if one (or more) pieces is in start
    def has_piece_inside(self):
        result = False
        for piece in self.pieces:
            if piece.position == -1:
                result = True
        return result

    # returns positions of all 4 pieces (with offset for comparison)
    def get_piece_positions_offset(self):
        positions = []
        for piece in self.pieces:
            # old:
            # positions.append(piece.get_realposition())
            positions.append(self.calculate_realposition(piece, 0))
        return positions

    def get_piece_positions(self):
        positions = []
        for piece in self.pieces:
            if piece.position == -1:
                positions.append("Start")
            else:
                positions.append(piece.position)
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

    def get_piece_on_start(self):
        for piece in self.pieces:
            if piece.position == 0:
                return piece
        return False

    def has_won(self):
        won = True
        for piece in self.pieces:
            if piece.position < self.parent.game_size:
                won = False
        return won

    def turn(self):
        print("Player", self.id+1, "Positions:", self.get_piece_positions())
        print("Player", self.id+1, "REAL Positions:", self.get_piece_positions_offset())

        piece_on_start = self.get_piece_on_start()
        if self.has_piece_outside():
            # normal game
            dice = self.roll_dice()
            if dice == 6:
                # bonus roll
                next_dice = self.roll_dice()
                if self.has_piece_inside():
                    if not piece_on_start:
                        i = input("Move Piece from home to board? (y/n)")
                        if i != "n":
                            self.place_piece_outside()
                            piece_on_start = self.get_piece_on_start()
                            if self.has_piece_inside():
                                # has to move from start
                                # TODO: check for kick and own pieces!
                                piece_on_start.go_forward(next_dice)
                            else:
                                self.move_freely(next_dice)
                        else:
                            self.move_freely(dice)
                            self.move_freely(next_dice)
                    else:
                        # has to move from start, TODO check for kick and own pieces
                        piece_on_start.go_forward(next_dice)
                else:
                    self.move_freely(dice)
                    self.move_freely(next_dice)

                if next_dice == 6:
                    # repeat
                    self.turn()
            else:
                self.move_freely(dice)
        else:
            # special case: roll 3 times
            for i in range(0, 3):
                print("Roll", i+1)
                dice = self.roll_dice()
                if dice == 6:
                    next_dice = self.roll_dice()
                    self.place_piece_outside()
                    self.get_piece_on_start().go_forward(next_dice)
                    if next_dice == 6:
                        self.turn()
                    break

    def move_freely(self, dice):
        i = int(input("Select Piece: "))
        #pos = self.pieces[i-1].position
        pos_real = self.calculate_realposition(self.pieces[i-1], 0)
        newpos_real = self.calculate_realposition(self.pieces[i-1], dice)

        # TODO: way to differentiate between the finishpoints
        if pos_real != "Start" and newpos_real != "Outside" and pos_real != "Finish":
            if self.is_field_free(newpos_real):
                self.pieces[i-1].go_forward(dice)
                # Man kann sich nicht selber rausschlagen und muss eine andere Figur nehmen.
                # TODO: was ist wenn das nicht möglich ist..?
        else:
            print("Cant move this piece")
            self.move_freely(dice)

    def roll_dice(self):
        dice = random.randint(1, 6)
        print("Rolling dice:", dice)
        return dice

    # check if field is free and kick other players if needed
    def is_field_free(self, realposition):
        free = True
        # return true for realposition == finish
        for player in self.parent.players:
            if player.id != self.id:
                for piece in player.pieces:
                    if piece.position < self.parent.game_size and piece.position != -1 and self.calculate_realposition(piece, 0) == realposition:
                        print("### kicking piece on position", realposition, " owner: player", player.id+1)
                        piece.position = -1
            else:
                for piece in player.pieces:
                    if self.calculate_realposition(piece, 0) == realposition and self.calculate_realposition(piece, 0) != "Finish":# and realposition is inside finish
                        print("Field is not free or outside the board")
                        free = False
        return free

    def calculate_realposition(self, piece, dice):
        position = piece.position + dice
        boardsize = self.parent.game_size

        # Check for start/finish
        if boardsize <= position <= boardsize+3:
            return "Finish"
        if position == -1:
            return "Start"
        if position > boardsize+3:
            return "Outside"

        # offset-calculation-wrap-around-magic
        if piece.parent.offset != 0:
            if position >= (boardsize-piece.parent.offset):
                return position - (boardsize-piece.parent.offset)
            else:
                return position + piece.parent.offset
        else:
            return position

    def set_name(self, name):
        self.name = name


class Piece:
    def __init__(self, parent):
        self.parent = parent
        self.position = -1

    def go_forward(self, distance):
        print("Moving piece from", self.position, "to", self.position + distance)
        self.position = self.position + distance
        print("Real new position:", self.parent.calculate_realposition(self, 0))


class Gamefield:
    def __init__(self, parent):
        self.parent = parent
        self.size = self.parent.game_size
        self.color = [colorama.Fore.RED, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.BLUE, colorama.Fore.MAGENTA, colorama.Fore.CYAN]
        self.color_reset = colorama.Fore.RESET
    
    def show(self, players):
        print ("Finish: ", end='')
        for player_index, player in enumerate(players):
            for piece_index, piece in enumerate(player.pieces):
                if "Finish" == player.calculate_realposition(piece, 0):
                    print(self.color[player_index] + str(piece_index+1) + self.color_reset, end='')
        print("")

        for i in reversed(range(0, self.size)):
            print (str(i) + ": ", end='')
            for player_index, player in enumerate(players):
                for piece_index, piece in enumerate(player.pieces):
                    if i == player.calculate_realposition(piece, 0):
                        print(self.color[player_index] + str(piece_index+1) + self.color_reset, end='')
            print("")


if __name__ == "__main__":
    # Start the game
    game = MenschAergereDichNicht(4)
    print(game.version)
