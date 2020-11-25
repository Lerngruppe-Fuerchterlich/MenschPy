# Mensch Ärgere Dich Nicht!
# created on 17.11.2020 by JPW

import random
import time


class MenschAergereDichNicht:
    # Class attribute
    version = "1.0"

    # Game
    def __init__(self, number_of_players):
        # instance attribute
        self.number_of_players = number_of_players
        self.players = []
        self.game_over = False

        print("starting...", self.number_of_players, "Players")

        for p in range(self.number_of_players):
            self.players.append(Player(self, p*10, p))

        while True:
            for player in self.players:
                print("")
                print("Players", player.id+1, "Turn")

                player.turn()

                if player.has_won():
                    print("Game Over")
                    print("Player", player.id+1, "has won")
                    return


class Player:
    def __init__(self, parent, offset, id):
        self.offset = offset
        self.pieces = []
        self.id = id
        self.parent = parent

        for x in range(0,4):
            self.pieces.append(Piece(self))

    # true if one (or more) pieces is on the board
    def has_piece_outside(self):
        result = False
        for piece in self.pieces:
            # todo: add check if piece is in the finish and cant move (to grant the player 3 dice rolls)
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
            if piece.position == -1:
                positions.append("Start")
            else:
                positions.append(piece.get_realposition())
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
    
    def has_won(self):
        won = True
        for piece in self.pieces:
            if piece.position < 40:
                won = False
        return won

    def turn(self):
        print("Player", self.id+1, "Positions:", self.get_piece_positions())
        print("Player", self.id+1, "REAL Positions:", self.get_piece_positions_offset())

        if self.has_piece_outside():
            # normal game
            dice = self.roll_dice()
            if dice == 6:
                # bonus roll
                next_dice = self.roll_dice()
                if self.has_piece_inside():
                    i = input("Move Piece from home to board? (y/n)")
                    if i != "n":
                        self.place_piece_outside()
                        if self.has_piece_inside():
                            # has to move from start
                            self.get_piece_on_start().go_forward(next_dice)
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
        if self.pieces[i-1].position != -1:
            if self.is_field_free(self.pieces[i-1].position+dice+self.offset):
                self.pieces[i-1].go_forward(dice)
            else:
                pass
                # todo: Spieler auffordern andere Figur zu nehmen
                # was ist wenn das nicht möglich ist..?
        else:
            print("Select a piece on the board!")
            self.move_freely(dice)

    def roll_dice(self):
        dice = random.randint(1, 6)
        print("Rolling dice:", dice)
        return dice

    # check if field is free and kick other players if needed
    def is_field_free(self, realposition):
        free = True
        for player in self.parent.players:
            if player.id != self.id:
                for piece in player.pieces:
                    if piece.position < 40 and piece.position != -1 and piece.position + player.offset == realposition:
                        print("Kicking out Player", player.id)
                        piece.position = -1
            else:
                for piece in player.pieces:
                    if piece.position + player.offset == realposition or realposition - player.offset > 43:
                        print("Field is not free or outside the board")
                        free = False
        return free


class Piece:
    def __init__(self, parent):
        self.position = -1
        self.parent = parent

    def go_forward(self, distance):
        new_position = self.position + distance
        print("Moving piece from", self.position, "to", new_position)
        self.position = new_position
        print("Real new position:", self.get_realposition())
        
    
    # get the real position of the piece on the board! implementing wrap around
    def get_realposition(self):
        boardsize = self.parent.parent.number_of_players*10
        if self.parent.offset != 0:
            if self.position >= (boardsize-self.parent.offset):
                return self.position - (boardsize-self.parent.offset)
            else:
                return self.position + self.parent.offset
        else:
            return self.position


if __name__ == "__main__":
    # Start the game
    game = MenschAergereDichNicht(4)
    print(game.version)
