import random
import math
import itertools
import time
import telebot
#15 14 ... check for message in user buffer 
class User:
    def __init__(self, chat_id, first_name, last_name,username,id,nickname):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.balance = 10000
        self.id = id
        self.nickname = nickname
class Poker_Table :
    def __init__(self,key,bot:telebot.TeleBot ,number_tables = 6,stack_size_bb = 200,game_type = "NL_Holdem",type ="private") -> None:
        self.number_tables = number_tables
        self.stack_size_bb = stack_size_bb
        self.game_type  = game_type
        self.buy_in_min = 20*stack_size_bb
        self.buy_in_max = 100*stack_size_bb
        self.type = type
        self.key = key
        self.bot = bot
        self.game = NL_Holdem(stack_size_bb,number_tables,bot)


class Player:
    nickname = ""
    current_table = None
    def __init__(self,user) -> None:
       self.nickname = user.nickname
       self.user = user
    
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
    def __init__(self,stack_size_bb,number_tables,bot:telebot.TeleBot) -> None:
        self.game_title = "Texas Hold'em"
        self.bottom = 0 
        self.pot = 0
        self.bot = bot
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
    def empty_tables_list(self) -> list:
      l = []
      for i in range(self.number_tables):
        if (self.tables[i] == False):
          l.append(i+1)
      return l
    def add_player (self,table_num,balance,player_obj:Player):
        self.players[table_num]=[balance,player_obj,False,"",""]
        self.num_players = self.num_players + 1
        self.game_status = self.game_status + 1
        self.tables[table_num] = True
        self.bot.send_message(player_obj.user.id,"message from add player function :)")
        # if (self.game_status == 2):
        #    self.deal_hand()

    def next_player(self,in_hand_players,p):
       for i in range(self.number_tables):
          if ((p+1+i)%self.number_tables in in_hand_players):
            return (p+1+i)%self.number_tables
          
    def bet(self,bets:list,player,amount):
       self.players[player][0] = self.players[player][0] - amount 
       bets[player] = bets[player] + amount
       self.pot = self.pot + amount 
       print(str(player)+" betted "+str(amount)," pot is "+str(self.pot)+"\n")

    def one_round_of_betting(self,cur_player,bets:list,in_hand_players:list,bet_amount,last_player_check):
       end_of_betting = False
       while(True):
          print(self.players[cur_player][0]," player balance  bet :",bet_amount)
          if (bet_amount >= self.players[cur_player][0]+bets[cur_player]):
             if(self.players[cur_player][0] ==  0):
               cur_player = self.next_player(in_hand_players,cur_player)
               if (cur_player == last_player_check):
                  break
               continue
             print("player" ,cur_player ,"all-in or fold")
             b = input()
             if (b.startswith("fold")):
                if(len(in_hand_players) == 2):
                  in_hand_players.remove(cur_player)
                  end_of_betting = True
                  break
                prv_player = cur_player
                cur_player = self.next_player(in_hand_players,cur_player)
                in_hand_players.remove(prv_player)
                if (cur_player == last_player_check):
                  break
             elif (b.startswith("all-in")):
                self.bet(bets,cur_player,self.players[cur_player][0])
                cur_player = self.next_player(in_hand_players,cur_player)
                if (cur_player == last_player_check):
                  break
                continue
             else:
                print("invalid input")
                continue
          elif(bet_amount == 0 or bet_amount == bets[cur_player]):
            print("player ",cur_player, "check or raise")
            b = input()
            if (b.startswith("check")):
              self.bet(bets,cur_player,0 )
              cur_player = self.next_player(in_hand_players,cur_player)
              if (cur_player == last_player_check):
                  break
            elif (b.startswith("raise")):
               new_bet
               if(b.startswith("raise all-in")):
                 new_bet = self.players[cur_player][0]
               else:
                 new_bet = int(b[6:])
               bet_amount = new_bet+bet_amount
               self.bet(bets,cur_player,new_bet)
               bet_amount = self.one_round_of_betting(self.next_player(in_hand_players,cur_player),bets,in_hand_players,bet_amount,cur_player)[0]
               break
            else:
                print("invalid input")
                continue
          else :
            print("player " ,cur_player , "fold or call or raise")
            b = input()
            if (b.startswith("fold")):
                if(len(in_hand_players) == 2):
                  in_hand_players.remove(cur_player)
                  end_of_betting = True
                  break
                prv_player = cur_player
                cur_player = self.next_player(in_hand_players,cur_player)
                in_hand_players.remove(prv_player)
                if (last_player_check == prv_player):
                  last_player_check = self.next_player(in_hand_players,prv_player)
                  continue
                if (cur_player == last_player_check):
                  break
            elif (b.startswith("call")):
               self.bet(bets,cur_player,bet_amount-bets[cur_player])
               cur_player = self.next_player(in_hand_players,cur_player)
               if (cur_player == last_player_check):
                  break
            elif (b.startswith("raise")):
               new_bet = 0
               if(b.startswith("raise all-in")):
                 new_bet = self.players[cur_player][0]
               else:
                 new_bet = int(b[6:])
               bet_amount = new_bet + bets[cur_player]
               self.bet(bets,cur_player,new_bet)
               bet_amount = self.one_round_of_betting(self.next_player(in_hand_players,cur_player),bets,in_hand_players,bet_amount,cur_player)[0]
               break
            else:
                print("invalid input")
                continue
       not_all_in_players = 0
       for p in in_hand_players:
         if(self.players[p][0] > 0 ):
          not_all_in_players += 1
       if (not_all_in_players <= 1) :
         end_of_betting = True
       return [bet_amount ,end_of_betting]
    


    def find_winner(self,table_cards:list,in_hand_players:list,bets:list):
        print(*bets)
        scores = [0]*self.num_players
        hands = []
        for i in range(self.num_players):
          hands.append([])
        for finial_players in in_hand_players :
          seven_cards = table_cards.copy()
          seven_cards.append(self.players[finial_players][3])
          seven_cards.append(self.players[finial_players][4])
          five_card_combs = (list(itertools.chain.from_iterable(itertools.combinations(seven_cards,r)for r in range(5,6))))
          max_point = 0
          max_hand = []
          for combs in five_card_combs :
            combs = sorted(combs,reverse=True)
            cur_point = self.isRoyal(combs)
            if(cur_point > max_point):
              max_point = cur_point
              max_hand = combs
          print(finial_players ,"best hand is :  ",*max_hand)
          scores[finial_players] = max_point
          hands[finial_players] = max_hand.copy()
        while(self.pot > 0):
          best_score = max(scores)
          winners = []
          for s in range(self.num_players) :
            if(scores[s] == best_score):
              winners.append(s)
          for p in winners :
            p_bet = bets[p]
            p_prize = 0.0
            for i in range(len(bets)):
              if (bets[i]>p_bet):
                bets[i] -= p_bet/len(winners)
                p_prize = p_prize + p_bet/len(winners)
              else:
                p_prize = p_prize + bets[i]/len(winners)
                bets[i] -= bets[i]/len(winners)
            self.players[p][0] += p_prize
            self.pot -= p_prize
            print("player ",p,"won",p_prize,"now pot is : ",self.pot)
          for p in winners :
            scores[p] = 0 

          
            
    def deal_hand(self):
        self.deck.shuffle()
        self.pot = 0.0
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
                  ##self.bet(bets, x, self.stack_size_bb)
                  self.players[x][2] = True

        for x in in_hand_players:
           p_cards = self.deck.deal_two()
           print ("player " + str(x) + " your cards are : ",p_cards[0],p_cards[1])
           self.players[x][3] =p_cards[0]
           self.players[x][4] =p_cards[1] 

      ## dael flop 

        flop_cards = self.deck.deal_three()
        turn_card = self.deck.deal_one()
        river_card = self.deck.deal_one()
        table_cards = [flop_cards[0],flop_cards[1],flop_cards[2],turn_card[0],river_card[0]]
        print ("flop is",flop_cards[0],flop_cards[1],flop_cards[2])
        first_round =self.one_round_of_betting(after_bigblind,bets,in_hand_players,self.stack_size_bb,after_bigblind)
        if(first_round[1]):
          if(len(in_hand_players) == 1):
            print("all folded player ",in_hand_players[0],"won pot",self.pot,"without showdown")
            self.players[in_hand_players[0]][0] += self.pot
            return
          else:
            print ("turn is",turn_card[0])
            print("river is",river_card[0])
            self.find_winner(table_cards,in_hand_players,bets)
            return
        else:
          print ("turn is",turn_card[0])
          if(smallblind not in in_hand_players):
            smallblind = self.next_player(in_hand_players,smallblind)
          second_round = self.one_round_of_betting(smallblind,bets,in_hand_players ,first_round[0],smallblind)
          if(second_round[1]):
            if(len(in_hand_players) == 1):
              print("all folded player ",in_hand_players[0],"won pot",self.pot,"without showdown")
              self.players[in_hand_players[0]][0] += self.pot
              return
            else:
              print("river is",river_card[0])
              self.find_winner(table_cards,in_hand_players,bets)
              return
          else: 
            print("river is",river_card[0])
            if(smallblind not in in_hand_players):
              smallblind = self.next_player(in_hand_players,smallblind)
            thrd_round = self.one_round_of_betting(smallblind,bets,in_hand_players,second_round[0],smallblind)
            if(thrd_round[1]):
              if(len(in_hand_players) == 1):
                print("all folded player ",in_hand_players[0],"won pot",self.pot,"without showdown")
                self.players[in_hand_players[0]][0] += self.pot
                return
              else:
                self.find_winner(table_cards,in_hand_players,bets)
                return
            else:
              self.find_winner(table_cards,in_hand_players,bets)                
            print("table cards :",*table_cards)
        




    def point(self,hand):                         #point()function to calculate partial score
      sortedHand=sorted(hand,reverse=True)
      c_sum=0
      ranklist=[]
      for card in sortedHand:
        ranklist.append(card.rank)
      c_sum=ranklist[0]*13**4+ranklist[1]*13**3+ranklist[2]*13**2+ranklist[3]*13+ranklist[4]
      return c_sum

        
    def isRoyal (self, hand):               #returns the total_point and prints out 'Royal Flush' if true, if false, pass down to isStraightFlush(hand)
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=10
      Cursuit=sortedHand[0].suit
      Currank=14
      total_point=h*13**5+self.point(sortedHand)
      for card in sortedHand:
        if card.suit!=Cursuit or card.rank!=Currank:
          flag=False
          break
        else:
          Currank-=1
      if flag:
          #print('Royal Flush')
          return total_point
      else:
        return self.isStraightFlush(sortedHand)
      

    def isStraightFlush (self, hand):       #returns the total_point and prints out 'Straight Flush' if true, if false, pass down to isFour(hand)
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=9
      Cursuit=sortedHand[0].suit
      Currank=sortedHand[0].rank
      total_point=h*13**5+self.point(sortedHand)
      for card in sortedHand:
        if card.suit!=Cursuit or card.rank!=Currank:
          flag=False
          break
        else:
          Currank-=1
      if flag:
        #print ('Straight Flush')
        return total_point
      else:
        return self.isFour(sortedHand)

    def isFour (self, hand):                  #returns the total_point and prints out 'Four of a Kind' if true, if false, pass down to isFull()
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=8
      Currank=sortedHand[1].rank               #since it has 4 identical ranks,the 2nd one in the sorted listmust be the identical rank
      count=0
      total_point=h*13**5+self.point(sortedHand)
      for card in sortedHand:
        if card.rank==Currank:
          count+=1
      if not count<4:
        flag=True
        #print('Four of a Kind')
        return total_point

      else:
        return self.isFull(sortedHand)
      
    def isFull (self, hand):                     #returns the total_point and prints out 'Full House' if true, if false, pass down to isFlush()
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=7
      total_point=h*13**5+self.point(sortedHand)
      mylist=[]                                 #create a list to store ranks
      for card in sortedHand:
        mylist.append(card.rank)
      rank1=sortedHand[0].rank                  #The 1st rank and the last rank should be different in a sorted list
      rank2=sortedHand[-1].rank
      num_rank1=mylist.count(rank1)
      num_rank2=mylist.count(rank2)
      if (num_rank1==2 and num_rank2==3)or (num_rank1==3 and num_rank2==2):
        flag=True
        #print ('Full House')
        return total_point
        
      else:
        flag=False
        return self.isFlush(sortedHand)

    def isFlush (self, hand):                         #returns the total_point and prints out 'Flush' if true, if false, pass down to isStraight()
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=6
      total_point=h*13**5+self.point(sortedHand)
      Cursuit=sortedHand[0].suit
      for card in sortedHand:
        if not(card.suit==Cursuit):
          flag=False
          break
      if flag:
        #print ('Flush')
        return total_point
        
      else:
        return self.isStraight(sortedHand)

    def isStraight (self, hand):
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=5
      total_point=h*13**5+self.point(sortedHand)
      Currank=sortedHand[0].rank                        #this should be the highest rank
      for card in sortedHand:
        if card.rank!=Currank:
          flag=False
          break
        else:
          Currank-=1
      if flag:
        #print('Straight')
        return total_point
        
      else:
        return self.isThree(sortedHand)
          
    def isThree (self, hand):
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=4
      total_point=h*13**5+self.point(sortedHand)
      Currank=sortedHand[2].rank                    #In a sorted rank, the middle one should have 3 counts if flag=True
      mylist=[]
      for card in sortedHand:
        mylist.append(card.rank)
      if mylist.count(Currank)==3:
        flag=True
        #print ("Three of a Kind")
        return total_point
        
      else:
        flag=False
        return self.isTwo(sortedHand)
          
    def isTwo (self, hand):                           #returns the total_point and prints out 'Two Pair' if true, if false, pass down to isOne()
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=3
      total_point=h*13**5+self.point(sortedHand)
      rank1=sortedHand[1].rank                        #in a five cards sorted group, if isTwo(), the 2nd and 4th card should have another identical rank
      rank2=sortedHand[3].rank
      mylist=[]
      for card in sortedHand:
        mylist.append(card.rank)
      if mylist.count(rank1)==2 and mylist.count(rank2)==2:
        flag=True
        #print ("Two Pair")
        return total_point
        
      else:
        flag=False
        return self.isOne(sortedHand)
    
    def isOne (self, hand):                            #returns the total_point and prints out 'One Pair' if true, if false, pass down to isHigh()
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=2
      total_point=h*13**5+self.point(sortedHand)
      mylist=[]                                       #create an empty list to store ranks
      mycount=[]                                      #create an empty list to store number of count of each rank
      for card in sortedHand:
        mylist.append(card.rank)
      for each in mylist:
        count=mylist.count(each)
        mycount.append(count)
      if mycount.count(2)==2 and mycount.count(1)==3:  #There should be only 2 identical numbers and the rest are all different
        flag=True
        #print ("One Pair")
        return total_point
        
      else:
        flag=False
        return self.isHigh(sortedHand)

    def isHigh (self, hand):                          #returns the total_point and prints out 'High Card' 
      sortedHand=sorted(hand,reverse=True)
      flag=True
      h=1
      total_point=h*13**5+self.point(sortedHand)
      mylist=[]                                       #create a list to store ranks
      for card in sortedHand:
        mylist.append(card.rank)
      #print ("High Card")
      return total_point




# n = NL_Holdem(200,6)
# hamid = Player("harry")
# parnaz = Player("pary")
# mohsen = Player("msn")
# sina = Player("Qane")
# darya = Player("kenar")
# amir = Player("dawsham")
# n.add_player(0,2000,hamid)
# n.add_player(1,3000,parnaz)
# n.add_player(2,4000,mohsen)
# n.add_player(3,5000,sina)
# n.deal_hand()