import requests
import rich
class PlayerReader:
    def __init__(self,url):
        self.url = url

    def get_players(self):
        response = requests.get(self.url).json()
        players = []

        for player_dict in response:
            player = Player(player_dict)
            players.append(player)
        return players


class PlayerStats:
    def __init__(self,reader: PlayerReader):
        self.players = reader.get_players()

    def top_scorers_by_nationality(self, nationality):
        filtered = [player for player in self.players if player.nationality==nationality]
        return sorted(filtered, key=lambda player: player.points, reverse=True)

class Player:
    def __init__(self, dict):
        self.name = dict['name']
        self.nationality = dict['nationality']
        self.goals = dict['goals']
        self.assists = dict['assists']
        self.team = dict['team']
        self.games = dict['games']
        self.points = self.goals+self.assists
    
    def __str__(self):
        return (self.name,self.team,self.goals,self.assists,self.points)
    
    def to_row(self):
        return (self.name,self.team,str(self.goals),str(self.assists),str(self.points))
