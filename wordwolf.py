import random
import numpy as np
import copy

class WordWolf():
    
    def __init__(self,):
        self.state="accepting_player"
        self.players=[]
        self.seed=random.randint(0,10000000000000000)
        self.wolf_size=1
        self.info={}
        self.theme=None

    def kill(self):
        self.state="accepting_player"
        self.players=[]
        self.seed=random.randint(0,10000000000000000)
        self.wolf_size=1
        self.info={}
        self.theme=None
        
    def add_player(self,player_name):
        if self.state!="accepting_player":
            return("this is not a time")
        if player_name in self.players:
            return("this player is already registrated.")
        self.players.append(player_name)
        print("self.players:",self.players)
        return len(self.players)
    
    def remove_player(self,player_name):
        if self.state!="accepting_player":
            return("this is not a time")
        if player_name not in self.players:
            return("this player is not registrated.")
        self.players.remove(player_name)
        return len(self.players)
    
    def reset_player(self):
        if self.state!="accepting_player":
            return("this is not a time")
        self.players=[]
        return len(self.players)
    
    def set_seed(self,new):
        if self.state!="accepting_player":
            return("this is not a time")
        self.seed=new
        print("SEEDnewseed",self.seed)
        return(self.seed)
    
    def set_wolf_size(self,new):
        if self.state!="accepting_player":
            return("this is not a time")
        self.wolf_size=new
        return(self.wolf_size)
    
    def start(self,):
        print("STARTnewseed",self.seed)
        if self.state!="accepting_player":
            return("this is not a time")
        
        self.player_size=len(self.players)
        
        #choose wolf randomly
        random.seed(self.seed)
        self.wolfs=random.sample(self.players,self.wolf_size)
        
        #choose theme
        self.theme=self.choose_theme()
        
        #create player_info
        self.initialize_info()
        
        self.state="theme_discussion"
        self.unvoters=copy.deepcopy(self.players)
        
        return self.players,self.wolfs,self.theme

    def initialize_info(self):
        self.info={"players":{},"game":{}}
        for i in self.players:
            role="villager"
            if i in self.wolfs:
                role="wolf"
            self.info["players"][i]={"role":role,"vote":"","count":0}
            
            self.info["game"]={"seed":self.seed,
                               "theme":self.theme,
                               "valid_targets":copy.deepcopy(self.players),
                                "valid_voters":copy.deepcopy(self.players)}
        #print(self.players)

    def show_info(self):
        print(self.info)
        print("seed:",self.seed)
        print("theme:",self.theme)
        print("state:",self.state)
    
    def get_info(self):
        return self.info

    
    def vote(self,who,target):
        if self.state!="theme_discussion":
            return("this is not a time")
        """
        if target not in self.players:
            print(self.players)
            return("target is not here.")
        if who not in self.players:
            return("voter is not here.")
        """
        if target not in self.info["game"]["valid_targets"]:
            return("target is not valid.")
        if who not in self.info["game"]["valid_voters"]:
            return("you cannot vote.")
        self.info["players"][who]["vote"]=target
        if who in self.unvoters:
            self.unvoters.remove(who)
        #print(self.players)
        return "OK"
        
    def execute(self):
        if self.state!="theme_discussion":
            return("this is not the time","","")
        #reset vote count
        for player,value in self.info["players"].items():
            #print(player)
            value["count"]=0
        #count votes
        unvoters=[]
        for player,value in self.info["players"].items():
            if player not in self.info["game"]["valid_voters"]:
                continue
            #print(player)
            target=value["vote"]
            if target == "":
                unvoters.append(player)
            else:
                self.info["players"][target]["count"]+=1
                
        if unvoters!=[]:
            self.please_vote(self.unvoters)
            return "Unvoters",len(unvoters),""
        
        #全員の投票が確認できたら
        max_vote=0
        target=[]
        for player,value in self.info["players"].items():
            if value["count"]>max_vote:
                target=[player]
                max_vote=value["count"]
            elif value["count"]==max_vote:
                target.append(player)
                
        if len(target)==1:
            #successfully executed
            target=target[0]
            winner=""
            if self.info["players"][target]["role"]=="villager":
                winner="wolf"
            else:
                winner="villager"
            self.state="accepting_player"
            self.seed=random.randint(0,10000000000000000)
            return "Finish",target,self.info["players"][target]["role"]
        else:
            #同数
            self.info["game"]["valid_targets"]=target
            self.info["game"]["valid_voters"]=list(set(self.players)-set(target))
            if self.info["game"]["valid_voters"]==[]:
                self.info["game"]["valid_voters"]=copy.deepcopy(self.info["game"]["valid_targets"])
            return "Tie",target,""
            
    def please_vote(self,unvoters):
        print("please vote!!")
        return "please vote submitted"
    
    
    def choose_theme(self):
        import urllib.request
        import json

        url="https://script.googleusercontent.com/macros/echo?user_content_key=i3z76bFOz8iIjZ5dHrBcwbfshfIaIGSnF6Y9j_epFVRe3slY9H0XRNsh4ruo36zFOpERU1LB3OciRvl34Tt8tweVFjvZ3Guom5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnENWYSltCZEqc2fMYoBs9hRli2s7R0Z_TbSdVuungFPbICE_M3iNgHRnXATAJX6NK0WY2nZ7HPw5&lib=Mztrc9W5LTtr3Ej5KTg37XEhPlfSlk_n8"
        data=""
        with urllib.request.urlopen(url) as r:
            data=r.read().decode("utf-8")

        data=json.loads(data)
        data = list(filter(lambda str:str != '', data))
        row,col=np.array(data).shape
        #print(row,col)
        for i in range(row):
            data[i] = list(filter(lambda str:str != '', data[i]))

        #pprint(data)

        
        random.seed(self.seed)
        theme=random.sample(data,1)
        #print(theme)
        theme=random.sample(theme[0][1:],2)
        #print(theme)

        return theme