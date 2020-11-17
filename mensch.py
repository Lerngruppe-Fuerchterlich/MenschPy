# Mensch Ärgere Dich Nicht!
# created on 17.11.2020 by JPW

import random


class MenschAergereDichNicht:
    # Class attribute
    version = "0.1"

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
                if player.has_piece_outside():
                    dice = player.roll_dice()
                    player.move(dice)
                else:
                    # 3mal würfeln
                    for i in range(0, 3):
                        print("Roll", i+1)
                        dice = player.roll_dice()
                        if dice == 6:
                            player.move(dice)
                            break

                if player.has_won():
                    print("Game Over")
                    print("Player", player.id+1, "has won")
                    return

    # set pieces on position back to the start
    def seek_and_destroy(self, position):
        for player in self.players:
            for piece in player.pieces:
                if piece.position == position+player.offset:
                    print("Kicking out Player", player.id)
                    piece.position = -1


class Player:
    def __init__(self, parent, offset, id):
        self.offset = offset
        self.pieces = []
        self.id = id
        self.parent = parent

        for x in range(0,4):
            self.pieces.append(Piece())

    # true if one (or more) pieces is on the playfield
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
                positions.append(piece.position+self.offset)
        return positions

    def get_piece_positions(self):
        positions = []
        for piece in self.pieces:
            if piece.position == -1:
                positions.append("Start")
            else:
                positions.append(piece.position)
        return positions

    # move piece from start area to playfield
    def place_piece_outside(self):
        for piece in self.pieces:
            if piece.position == -1:
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

    def move(self, dice):
        print("Player", self.id+1, "Positions:", self.get_piece_positions())
        # spieler hat eine 6 gewürfelt
        if dice == 6:
            # bonus roll
            next_dice = self.roll_dice()
            if not self.has_piece_outside():
                self.place_piece_outside()
                self.get_piece_on_start().go_forward(next_dice)
            elif self.has_piece_inside():
                i = input("Move Piece onto playfield? (y/n)")
                if i == "y":
                    self.place_piece_outside()
                    if self.has_piece_inside():
                        # has to move from start
                        self.get_piece_on_start().go_forward(next_dice)
                else:
                    self.move_freely(next_dice)
            # repeat everything if another 6
            if next_dice == 6:
                self.move(next_dice)
        else:
            self.move_freely(dice)

    def move_freely(self, dice):
        i = int(input("Select Piece: "))
        self.pieces[i-1].go_forward(dice)

    def roll_dice(self):
        dice = random.randint(1, 6)
        print("Rolling dice:", dice)
        return dice


class Piece:
    def __init__(self):
        self.position = -1

    def go_forward(self, distance):
        self.position += distance
        print("Moving piece to", self.position)



if __name__ == "__main__":
    # Start the game
    game = MenschAergereDichNicht(4)
    print(game.version)
