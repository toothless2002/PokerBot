import random



class Poker_Table :
    def __init__(self,number_tables = 6,stack_size_bb = 200,game_type = "NL_Holdem") -> None:
        self.number_tables = number_tables
        self.stack_size_bb = stack_size_bb
        self.game_type  = game_type
        self.buy_in_min = 20*stack_size_bb
        self.buy_in_max = 100*stack_size_bb
        


class Player:
    total_balance  = 0 
    nickname = ""
    current_table = None
    def __init__(self,nickname) -> None:
       self.nickname = nickname
    def inc_balance(self,amount):
       self.total_balance = self.total_balance + amount
       return self.total_balance
    
class Suit:
    CLUBS = "♣", "C", "Clubs"
    DIAMONDS = "♦", "D", "Diamonds"
    HEARTS = "♥", "H", "Hearts"
    SPADES = "♠", "S", "Spades"

class Rank:
    DEUCE = "2", 2
    THREE = "3", 3
    FOUR = "4", 4
    FIVE = "5", 5
    SIX = "6", 6
    SEVEN = "7", 7
    EIGHT = "8", 8
    NINE = "9", 9
    TEN = "T", 10
    JACK = "J",11
    QUEEN = "Q",12
    KING = "K",13
    ACE = "A", 14

class Card :
  RANKS = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)

  SUITS = ('S', 'D', 'H', 'C')

  def __init__ (self, rank, suit):
    self.rank = rank
    self.suit = suit

  def __str__ (self):
    if self.rank == 14:
      rank = 'A'
    elif self.rank == 13:
      rank = 'K'
    elif self.rank == 12:
      rank = 'Q'
    elif self.rank == 11:
      rank = 'J'
    else:
      rank = self.rank
    return str(rank) + self.suit

  def __eq__ (self, other):
    return (self.rank == other.rank)

  def __ne__ (self, other):
    return (self.rank != other.rank)

  def __lt__ (self, other):
    return (self.rank < other.rank)

  def __le__ (self, other):
    return (self.rank <= other.rank)

  def __gt__ (self, other):
    return (self.rank > other.rank)

  def __ge__ (self, other):
    return (self.rank >= other.rank)


class Deck :
  def __init__ (self):
    self.deck = []
    self.current_card = 0 
    for suit in Card.SUITS:
      for rank in Card.RANKS:
        card = Card (rank, suit)
        self.deck.append(card)

  def shuffle (self):
    random.shuffle (self.deck)
    self.current_card = 0 
  def __len__ (self):
    return len (self.deck)

  def deal (self)-> str:
    if len(self) == 0:
      return None
    else:
      return self.deck.pop(0)
  def deal_one(self):
     self.current_card = self.current_card+1
     return [self.deck[self.current_card-1]]
  def deal_two(self):
     self.current_card = self.current_card+2
     return [self.deck[self.current_card-2],self.deck[self.current_card-1]]
  def deal_three(self):
     self.current_card = self.current_card+3
     return [self.deck[self.current_card-3],self.deck[self.current_card-2],self.deck[self.current_card-1]]


class NL_Holdem:
    def __init__(self,stack_size_bb,number_tables) -> None:
        self.bottom = 0 
        self.pot = 0 
        ############################################        neeed to make multi pot 
        self.num_players = 0 
        self.game_status = 0
        self.deck = Deck()
        # 0 "not started 0 player"
        # 1 "not started 1 player"
        # 2 "first hand of the table"
        # 3 "in a hand"
        # 4 "in a hand new player joined"
        
        self.stack_size_bb = stack_size_bb
        self.number_tables = number_tables
        self.tables = [False]*number_tables
        self.players = [None]*number_tables

    def empty_tables(self) -> int:
        sum = 0 
        for i in range(self.number_tables):
            if (self.tables[i] == False):
                sum = sum + 1
        return sum
    
    def add_player (self,table_num,balance,player_obj:Player):
        self.players[table_num]=[balance,player_obj,False,"",""]
        self.num_players = self.num_players + 1
        self.game_status = self.game_status + 1
        if (self.game_status == 2):
           self.deal_hand()

    def next_player(self,in_hand_players,p):
       for i in in_hand_players:
          if (i == p ):
            return (i+1)% len(in_hand_players)
          
    def bet(self,bets:list,player,amount):
       self.players[player][0] = self.players[player][0] - amount 
       bets[player] = bets[player] + amount
       self.pot = self.pot + amount 
       print(str(player)+" betted "+str(amount)," pot is "+str(self.pot)+"\n")

    def one_round_of_betting(self,cur_player,bets:list,in_hand_players):
       start_player = cur_player
       while(True):
          print("player " ,cur_player , " put in your bet\n")
          b = int(input())
          self.bet(bets,cur_player,b)
          cur_player = self.next_player(in_hand_players,cur_player)
          if (cur_player == start_player):
             break

    def deal_hand(self):
        self.deck.shuffle()
        self.pot = 0 
        bets = [0]*self.num_players
        in_hand_players = []
        in_hand_players_num = 0
        for p in range(self.num_players):
          if (self.players[p] != None):
             in_hand_players.append(p)
             in_hand_players_num = in_hand_players_num + 1 
        if(self.game_status == 2):        
            self.bottom = random.choices(in_hand_players)[0]
            self.game_status = 3

        print(in_hand_players,self.bottom)
        smallblind = self.next_player(in_hand_players,self.bottom)
        self.bet(bets, smallblind, self.stack_size_bb/2)
        bigblind = self.next_player(in_hand_players,smallblind)
        self.bet(bets, bigblind, self.stack_size_bb)
        after_bigblind = self.next_player(in_hand_players,bigblind)
              
        if(self.game_status == 4):        
            for x in in_hand_players:
              if (self.players[x][2] == False):
                  self.bet(bets, x, self.stack_size_bb)
                  self.players[x][2] = True

        for x in in_hand_players:
           p_cards = self.deck.deal_two()
           print ("player " + str(x) + " your cards are : ",p_cards[0],p_cards[1])
           self.players[x][3] =p_cards[0]
           self.players[x][4] =p_cards[1]
           
        
      ## dael flop 
        flop_cards = self.deck.deal_three()
        print ("flop is",flop_cards[0],flop_cards[1],flop_cards[2])
        self.one_round_of_betting(after_bigblind,bets,in_hand_players)
        turn_card = self.deck.deal_one()
        print ("turn is",turn_card[0])
        self.one_round_of_betting(smallblind,bets,in_hand_players)
        river_card = self.deck.deal_one()
        print("river is",river_card[0])
        self.one_round_of_betting(smallblind,bets,in_hand_players)



n = NL_Holdem(200,6)
hamid = Player("harry")
parnaz = Player("pary")
mohsen = Player("msn")
n.add_player(0,2000,hamid)
n.add_player(1,2000,parnaz)
