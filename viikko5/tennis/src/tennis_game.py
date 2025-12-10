class TennisGame:
    def __init__(self, player1_name, player2_name):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.m_score1 = 0
        self.m_score2 = 0

    def won_point(self, player_name):
        if player_name == "player1":
            self.m_score1 += 1
        else:
            self.m_score2 += 1

    def equal_score(self):
        if self.m_score1 == 0:
            return "Love-All"
        elif self.m_score1 == 1:
            return "Fifteen-All"
        elif self.m_score1 == 2:
            return "Thirty-All"
        else:
            return "Deuce"

    def end_of_point(self):
        minus_result = self.m_score1 - self.m_score2

        if minus_result == 1:
            return "Advantage player1"
        elif minus_result == -1:
            return "Advantage player2"
        elif minus_result >= 2:
            return "Win for player1"
        else:
            return "Win for player2"

    def normal_play_score(self):
        score = ""
        temp_score = 0

        for i in range(1, 3):
            if i == 1:
                temp_score = self.m_score1
            else:
                score += "-"
                temp_score = self.m_score2

            if temp_score == 0:
                score += "Love"
            elif temp_score == 1:
                score += "Fifteen"
            elif temp_score == 2:
                score += "Thirty"
            elif temp_score == 3:
                score += "Forty"

        return score
#For test pr
    def get_score(self):
        if self.m_score1 == self.m_score2:
            return self.equal_score()

        elif self.m_score1 >= 4 or self.m_score2 >= 4:
            return self.end_of_point()

        else:
            return self.normal_play_score()
