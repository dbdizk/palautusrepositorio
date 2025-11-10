import requests
from player import Player, PlayerReader, PlayerStats
from rich.console import Console
from rich.table import Table



def main(season,nationality):
    url = f"https://studies.cs.helsinki.fi/nhlstats/{season}/players"
    reader = PlayerReader(url)
    stats = PlayerStats(reader)
    players = stats.top_scorers_by_nationality(nationality)

    table = Table(title=f"Season {season} players from {nationality}")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Teams")
    table.add_column("Goals")
    table.add_column("Assists")
    table.add_column("Points")

    for player in players:
        table.add_row(*player.to_row())

    console = Console()
    console.print(table)
    
if __name__ == "__main__":
    season = input("Enter season (format '2020-21'): ")
    nationality = input("Enter nationality (format 'FIN, USA'): ")
    main(season,nationality)
